import asyncio
import traceback
from base64 import b64decode
from collections import defaultdict
from datetime import datetime
from functools import partial

import pandas as pd
import pygsheets
from fastapi import Depends
from pygsheets import PyGsheetsException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3

from app.consts import NATIVE_TOKEN_ADDRESS
from app.crud.profiles import ProfilesCrud
from app.crud.transactions import TransactionsCrud
from app.services import Crypto
from app.services.launchpad.abi import LAUNCHPAD_CONTRACT_ADDRESS_ABI
from app.base import logger, engine
from app.common import Command, CommandResult
from app.crud import LaunchpadProjectCrud
from app.crud.launchpad_events import LaunchpadContractEventsCrud
from app.dependencies import (
    get_launchpad_contract_events_crud,
    get_launchpad_projects_crud,
    get_transactions_crud,
    get_profile_crud,
    get_launchpad_crypto,
    get_add_points,
    get_redis,
)
from app.env import settings
from app.models import (
    LaunchpadContractEventType,
    TransactionPaymentMethod,
    OperationType,
    LaunchpadEventProjectType,
    StatusProject,
    ProjectType,
)
from app.schema import CreateLaunchpadEvent, CreateLaunchpadTransactionParams
from app.services.launchpad.redis_cli import (
    launchpad_events_cache,
    launchpad_multichain_events_cache,
)
from app.services.launchpad.types import LaunchpadTransaction, BuyTokensInput
from app.services.launchpad.utils import CoinTypeResolver, get_crypto_contracts
from app.services.points.add_points import AddPoints
from app.services.points.calculator import PointsCalculator
from app.services.prices import get_tokens_price_for_chain
from app.services.web3_nodes import web3_node
from app.utils import get_data_with_cache


class ProcessLaunchpadContractEvents(Command):
    async def get_all_events_and_save_to_gs(
        self, crud: LaunchpadContractEventsCrud, project_crud: LaunchpadProjectCrud
    ):
        if not settings.google_service_account_json:
            logger.error("Process launchpad events: google_service_account_json not set")
            return
        data = defaultdict(list)
        async with engine.begin() as conn:
            events = await crud.get_all_events(conn)
            info_by_contract_project_id = (
                await project_crud.get_project_info_by_contract_project_id(conn)
            )
            tier_info = await crud.get_tier_by_user_address_and_contract_project_id(conn)

            for event in events:
                contr_project_id = event.contract_project_id
                tier = event.extra.get("tier")
                project_name = info_by_contract_project_id.get(contr_project_id, {}).get("name", "")
                tokens_amount = round(Web3.from_wei(int(event.extra.get("amount", 0)), "ether"), 6)
                token_price = info_by_contract_project_id.get(contr_project_id, {}).get("price", 0)
                usd_amount = round(tokens_amount * token_price, 2)
                if (
                    event_type := event.event_type.value
                ) == LaunchpadContractEventType.USER_REGISTERED.value:
                    tokens_amount, usd_amount, token_price = "", "", ""
                elif event_type == LaunchpadContractEventType.TOKENS_BOUGHT.value:
                    tier = tier_info.get(f"{event.user_address.lower()}_{contr_project_id}")

                data["#"].append(event.id)
                data["event_type"].append(event_type)
                data["project_name"].append(project_name)
                data["contract_project_id"].append(contr_project_id)
                data["tokens_amount"].append(tokens_amount)
                data["usd_token_price"].append(token_price)
                data["usd_amount"].append(usd_amount)
                data["tier"].append(tier + 1 if tier is not None else "")
                data["user_address"].append(event.user_address)
                data["token_address"].append(event.token_address)
                data["txn_hash"].append(event.txn_hash)
                data["block_number"].append(event.block_number)
                data["created_at"].append(event.created_at)
        dataframe = pd.DataFrame(data)

        gc = pygsheets.authorize(
            service_account_json=b64decode(settings.google_service_account_json),
        )
        try:
            sh = gc.open(settings.google_launchpad_events_report_filename)
            sh[0].set_dataframe(dataframe, (1, 1))
            filename = settings.google_launchpad_events_report_filename
            logger.info(f"Saved launchpad events report to {filename}")
        except PyGsheetsException as exc:
            logger.error(f"Process launchpad events: gs exception: {str(exc)}")

    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
        project_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
    ) -> CommandResult:
        if not settings.launchpad_contract_address:
            logger.error("Process launchpad events: launchpad contract address is not set")
            return CommandResult(success=False, need_retry=False)

        web3 = await web3_node.get_web3(network="blast")
        chain_id = await web3.eth.chain_id
        current_block = await web3.eth.block_number
        log = f"Process launchpad events: {settings.launchpad_contract_address=}, {chain_id=}, {current_block=}"  # noqa
        logger.info(log)
        if (
            last_checked_block := await launchpad_events_cache.get_last_checked_block(chain_id)
        ) is None:
            last_checked_block = current_block - 100_000

        if last_checked_block >= current_block:
            return CommandResult(success=True, need_retry=False)

        while True:
            from_block = last_checked_block + 1
            # 3000 is limit, can't set larger than that
            to_block = min(current_block, from_block + 3000)
            logger.info(f"Monitoring launchpad events from {from_block} to {to_block}")

            if from_block > to_block:
                logger.info(f"No launchpad events from {from_block} to {to_block}")
                break

            from app.tasks import monitor_and_save_launchpad_events

            monitor_and_save_launchpad_events.apply_async(
                kwargs={
                    "from_block": from_block,
                    "to_block": to_block,
                    "chain_id": chain_id,
                },
                countdown=1,
            )

            last_checked_block = to_block
            await launchpad_events_cache.set_last_checked_block(chain_id, to_block)
            await asyncio.sleep(0.5)

        # await self.get_all_events_and_save_to_gs(crud, project_crud)

        return CommandResult(success=True, need_retry=False)


class MonitorMultichainLaunchpadLogAndSave(Command):
    def __init__(
        self, from_block: int, to_block: int, chain_id: int, contract_address: str, project_id: str
    ) -> None:
        self.from_block = from_block
        self.to_block = to_block
        self.chain_id = chain_id
        self.contract_address = contract_address
        self.project_id = project_id

    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        crypto: Crypto = Depends(get_launchpad_crypto),
    ) -> CommandResult:
        str_network = crypto.get_network_by_chain_id(self.chain_id)
        try:
            contract = await crypto.presale_contract(str_network, self.contract_address)
            tokens_bought_events = await contract.events.TokensBought().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            if not tokens_bought_events:
                logger.info(
                    f"No multichain events for {self.contract_address}",
                    extra={
                        "from_block": self.from_block,
                        "to_block": self.to_block,
                    },
                )
                return CommandResult(success=True, need_retry=False)

            amount_and_usd_contract = await crypto.amount_and_usd_contract(
                str_network, self.contract_address
            )
            amount_and_usd_events = await amount_and_usd_contract.events.AmountAndUSD().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            token_amount = amount_and_usd_events[0].get("args", {}).get("amount", 0)
            usd_rate = amount_and_usd_events[0].get("args", {}).get("usd", 0) / 1e8

            tokens_bought_event = tokens_bought_events[0]
            txn_hash = tokens_bought_event.transactionHash.hex()
            user_address = tokens_bought_event.args["user"]
            await crud.add_event(
                params=CreateLaunchpadEvent(
                    user_address=user_address,
                    project_id=self.project_id,
                    project_type=LaunchpadEventProjectType.MULTICHAIN,
                    txn_hash=txn_hash,
                    chain_id=self.chain_id,
                    block_number=tokens_bought_event.blockNumber,
                    extra={"amount": str(token_amount)},
                    event_type=LaunchpadContractEventType.TOKENS_BOUGHT,
                )
            )
        except Exception as e:
            logger.error(
                f"Multichain launchpad logs error: {self.contract_address=} {self.project_id=}\n{str(e)}"  # noqa
            )
            return CommandResult(success=False, need_retry=True)

        from app.tasks import save_multichain_launchpad_txn_and_add_points

        save_multichain_launchpad_txn_and_add_points.apply_async(
            kwargs={
                "user_address": user_address,
                "txn_hash": txn_hash,
                "project_id": self.project_id,
                "token_amount": token_amount,
                "chain_id": self.chain_id,
                "usd_rate": usd_rate,
                "presale_contract_address": self.contract_address,
            }
        )
        return CommandResult(success=True, need_retry=False)


class SaveLaunchpadMultichainTransactionAndAddPoints(Command):
    def __init__(
        self,
        user_address: str,
        txn_hash: str,
        project_id: str,
        token_amount: int,
        chain_id: int,
        usd_rate: float,
        presale_contract_address: str,
    ) -> None:
        self.user_address = user_address.lower()
        self.project_id = project_id
        self.token_amount = token_amount
        self.txn_hash = txn_hash.lower()
        self.chain_id = chain_id
        self.currency2usd_rate = usd_rate
        self.presale_contract_address = presale_contract_address

    async def command(
        self,
        transactions_crud: TransactionsCrud = Depends(get_transactions_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        project_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        crypto: Crypto = Depends(get_launchpad_crypto),
        add_points: AddPoints = Depends(get_add_points),
    ) -> CommandResult:
        profile, _ = await profile_crud.get_or_create_profile(
            self.user_address, project_crud.session
        )
        project = await project_crud.find_by_id_or_slug(self.project_id)
        await project_crud.session.commit()

        if not project:
            logger.error(f"Launchpad project not found: {self.project_id=}")
            return CommandResult(success=False, need_retry=False)

        try:
            tx_data = await crypto.get_txn_data(chain_id=self.chain_id, tx_hash=self.txn_hash)
        except Exception as e:
            logger.error(f"Can't get txn data {self.chain_id} {self.txn_hash}: {e}")
            return CommandResult(success=False, need_retry=True)

        str_network = crypto.get_network_by_chain_id(self.chain_id)
        contract = await crypto.presale_contract(str_network, self.presale_contract_address)
        input = contract.decode_function_input(tx_data.get("input").hex())  # noqa

        is_native_token = CoinTypeResolver.is_native(input[0].fn_name)
        if is_native_token:
            value = tx_data.value / 1e18
            payment_token_address = NATIVE_TOKEN_ADDRESS
        else:
            usdt_decimals = {"eth": 6, "polygon": 6, "bsc": 18, "blast": 18}
            decimals = usdt_decimals[str_network]
            value = input[1].get("amount") / (10**decimals)
            payment_token_address = settings.blast_usdb_address

        payment_amount_usd = round(value * self.currency2usd_rate, 2)
        token_amount_usd = round(
            float(Web3.from_wei(self.token_amount, "ether") * project.token_price), 2
        )
        points_amount = PointsCalculator.calculate_points_for_ido_purchase(
            token_amount_usd, project.bonus_for_ido_purchase
        )

        async with AsyncSession(engine) as session:
            async with session.begin():
                referral_points_amount = 0
                if points_amount > 0:
                    await add_points.add_points(
                        address=profile.address,
                        amount=points_amount,
                        operation_type=OperationType.ADD,
                        project_id=project.id,
                        session=session,
                    )
                    if profile.referrer:
                        referral_points_amount = round(points_amount * profile.ref_percent / 100, 2)
                        await add_points.add_points(
                            address=profile.referrer,
                            amount=referral_points_amount,
                            operation_type=OperationType.ADD_REF,
                            project_id=project.id,
                            referring_profile_id=profile.id,
                            session=session,
                        )
                params = CreateLaunchpadTransactionParams(
                    project_id=project.id,
                    user_address=profile.address,
                    chain_id=self.chain_id,
                    hash=self.txn_hash,
                    payment_token_address=payment_token_address,
                    payment_amount=str(value),
                    payment_amount_usd=str(payment_amount_usd),
                    amount_project_token=str(self.token_amount),
                    currency2usd_rate=str(self.currency2usd_rate),
                    token2usd_rate=str(project.token_price),
                    method=TransactionPaymentMethod.CRYPTO.value,
                    confirmed_at=datetime.utcnow(),
                )
                if points_amount > 0:
                    params.points_amount = points_amount
                    params.ref_points_amount = referral_points_amount
                    params.points_paid_at = datetime.utcnow()
                await transactions_crud.add_transaction(params, session=session)

        return CommandResult(success=True, need_retry=False)


class MonitorLaunchpadLogsAndSave(Command):
    def __init__(self, from_block: int, to_block: int, chain_id: int) -> None:
        self.from_block = from_block
        self.to_block = to_block
        self.chain_id = chain_id

    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
    ) -> CommandResult:
        web3 = await web3_node.get_web3(network="blast")
        chain_id = await web3.eth.chain_id

        contract = web3.eth.contract(
            address=web3.to_checksum_address(settings.launchpad_contract_address),
            abi=LAUNCHPAD_CONTRACT_ADDRESS_ABI,
        )
        try:
            user_registered_events = await contract.events.UserRegistered().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            n_user_registered = len(user_registered_events)
            await self._save_user_registered_events(crud, chain_id, user_registered_events)

            tokens_bought_events = await contract.events.TokensBought().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            n_purchases = len(tokens_bought_events)
            tokens_bought_txns = await self._save_tokens_bought_events(
                crud, chain_id, tokens_bought_events
            )

            if any((n_user_registered, n_purchases)):
                logger.info(
                    f"Launchpad events: saving {n_user_registered=}, {n_purchases=}",
                    extra={
                        "from_block": self.from_block,
                        "to_block": self.to_block,
                    },
                )
                await crud.session.commit()
        except Exception as e:
            logger.error(
                f"Launchpad events: saving error:\n{e}  {traceback.format_exc()}",
                extra={
                    "from_block": self.from_block,
                    "to_block": self.to_block,
                },
            )
            return CommandResult(success=False, need_retry=True)

        if tokens_bought_txns:
            from app.tasks import save_launchpad_txn_and_add_points

            for i, txn in enumerate(tokens_bought_txns, start=1):
                save_launchpad_txn_and_add_points.apply_async(
                    kwargs={
                        "user_address": txn.user_address,
                        "txn_hash": txn.txn_hash,
                        "contract_project_id": txn.contract_project_id,
                        "token_amount": txn.token_amount,
                        "chain_id": txn.chain_id,
                    },
                    countdown=i,
                )

        return CommandResult(success=True, need_retry=False)

    async def _save_user_registered_events(
        self, crud: LaunchpadContractEventsCrud, chain_id: int, events
    ):
        for event in events:
            await crud.add_event(
                params=CreateLaunchpadEvent(
                    event_type=LaunchpadContractEventType.USER_REGISTERED,
                    token_address=event.args["token"],
                    user_address=event.args["user"],
                    txn_hash=event.transactionHash.hex(),
                    chain_id=chain_id,
                    contract_project_id=event.args["id"],
                    extra={"tier": event.args["tier"]},
                    block_number=event.blockNumber,
                )
            )

    async def _save_tokens_bought_events(
        self, crud: LaunchpadContractEventsCrud, chain_id: int, events
    ) -> list[LaunchpadTransaction]:
        txns = []
        for event in events:
            txn_hash = event.transactionHash.hex()
            user_address = event.args["buyer"]
            contract_project_id = event.args["id"]
            token_amount = str(event.args["amount"])
            await crud.add_event(
                params=CreateLaunchpadEvent(
                    event_type=LaunchpadContractEventType.TOKENS_BOUGHT,
                    token_address=event.args["token"],
                    user_address=user_address,
                    txn_hash=txn_hash,
                    chain_id=chain_id,
                    contract_project_id=contract_project_id,
                    extra={"amount": token_amount},
                    block_number=event.blockNumber,
                )
            )
            txns.append(
                LaunchpadTransaction(
                    user_address, txn_hash, contract_project_id, int(token_amount), chain_id
                )
            )
        return txns


class SaveLaunchpadTransactionAndAddPoints(Command):
    def __init__(
        self,
        user_address: str,
        txn_hash: str,
        contract_project_id: int,
        token_amount: int,
        chain_id: int,
    ) -> None:
        self.user_address = user_address.lower()
        self.contract_project_id = contract_project_id
        self.token_amount = token_amount
        self.txn_hash = txn_hash.lower()
        self.chain_id = chain_id

    async def command(
        self,
        transactions_crud: TransactionsCrud = Depends(get_transactions_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        project_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        crypto: Crypto = Depends(get_launchpad_crypto),
        add_points: AddPoints = Depends(get_add_points),
    ) -> CommandResult:
        profile, _ = await profile_crud.get_or_create_profile(self.user_address)
        project = await project_crud.find_by_contract_project_id(self.contract_project_id)
        await project_crud.session.commit()

        if not project:
            logger.error(f"Launchpad project not found: {self.contract_project_id=}")
            return CommandResult(success=False, need_retry=False)

        try:
            tx_data = await crypto.get_txn_data(chain_id=self.chain_id, tx_hash=self.txn_hash)
        except Exception as e:
            logger.error(f"Can't get txn data {self.chain_id} {self.txn_hash}: {e}")
            return CommandResult(success=False, need_retry=True)

        web3 = await web3_node.get_web3(chain_id=self.chain_id)
        contract = web3.eth.contract(
            address=web3.to_checksum_address(settings.launchpad_contract_address),
            abi=LAUNCHPAD_CONTRACT_ADDRESS_ABI,
        )
        decoded_input: BuyTokensInput = contract.decode_function_input(tx_data.get("input").hex())[
            1
        ]
        if (payment_token_address := decoded_input["paymentContract"]) == NATIVE_TOKEN_ADDRESS:
            payment_amount = tx_data.get("value")
        else:
            payment_amount = decoded_input["volume"]

        _payment_token_rate = await get_tokens_price_for_chain(
            self.chain_id, [payment_token_address]
        )
        if not _payment_token_rate:
            logger.error(
                f"Can't get payment token rate for {self.chain_id}, {payment_token_address=}"
            )
            return CommandResult(success=False, need_retry=True)
        currency2usd_rate = _payment_token_rate.get(payment_token_address.lower())
        payment_amount_usd = round(
            float(web3.from_wei(payment_amount, "ether")) * currency2usd_rate, 2
        )
        token_amount_usd = float(web3.from_wei(self.token_amount, "ether") * project.token_price)
        points_amount = PointsCalculator.calculate_points_for_ido_purchase(
            token_amount_usd, project.bonus_for_ido_purchase
        )

        async with AsyncSession(engine) as session:
            async with session.begin():
                referral_points_amount = 0
                if points_amount > 0:
                    await add_points.add_points(
                        address=profile.address,
                        amount=points_amount,
                        operation_type=OperationType.ADD,
                        project_id=project.id,
                        session=session,
                    )
                    if profile.referrer:
                        referral_points_amount = round(points_amount * profile.ref_percent / 100, 2)
                        await add_points.add_points(
                            address=profile.referrer,
                            amount=referral_points_amount,
                            operation_type=OperationType.ADD_REF,
                            project_id=project.id,
                            referring_profile_id=profile.id,
                            session=session,
                        )
                params = CreateLaunchpadTransactionParams(
                    project_id=project.id,
                    user_address=profile.address,
                    chain_id=self.chain_id,
                    hash=self.txn_hash,
                    payment_token_address=payment_token_address,
                    payment_amount=str(payment_amount),
                    payment_amount_usd=str(payment_amount_usd),
                    amount_project_token=str(self.token_amount),
                    currency2usd_rate=str(currency2usd_rate),
                    token2usd_rate=str(project.token_price),
                    method=TransactionPaymentMethod.CRYPTO.value,
                    confirmed_at=datetime.utcnow(),
                )
                if points_amount > 0:
                    params.points_amount = points_amount
                    params.ref_points_amount = referral_points_amount
                    params.points_paid_at = datetime.utcnow()
                await transactions_crud.add_transaction(params, session=session)

        return CommandResult(success=True, need_retry=False)


class ProcessMultichainLaunchpadContractEvents(Command):
    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
        project_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis),
    ) -> CommandResult:
        ongoing_multichain_projects = await project_crud.all(
            status=StatusProject.ONGOING, project_type=ProjectType.PRIVATE_PRESALE
        )
        for project in ongoing_multichain_projects:
            project_contracts: dict[str, str] | None = await get_data_with_cache(
                key=f"project_contracts_{project.slug}",
                func=partial(get_crypto_contracts, project.proxy_link.base_url),
                redis=redis,
                short_key_exp_seconds=60,
                long_key_exp_minutes=60,
            )
            project_contracts = project_contracts or {}
            for network, contract_address in project_contracts.items():
                web3 = await web3_node.get_web3(network=network)
                chain_id = await web3.eth.chain_id
                current_block = await web3.eth.block_number
                log = f"Process multichain launchpad events: {contract_address=}, {chain_id=}, {current_block=}"  # noqa
                logger.info(log)
                if (
                    last_checked_block := await launchpad_multichain_events_cache.get_last_checked_block(  # noqa
                        chain_id, contract_address
                    )
                ) is None:
                    last_checked_block = current_block - 100_000

                if last_checked_block >= current_block:
                    return CommandResult(success=True, need_retry=False)

                while True:
                    from_block = last_checked_block + 1
                    # 3000 is limit, can't set larger than that
                    to_block = min(current_block, from_block + 3000)
                    logger.info(f"Monitoring launchpad events from {from_block} to {to_block}")

                    if from_block > to_block:
                        logger.info(f"No launchpad events from {from_block} to {to_block}")
                        break

                    from app.tasks import monitor_and_save_multichain_launchpad_events

                    monitor_and_save_multichain_launchpad_events.apply_async(
                        kwargs={
                            "from_block": from_block,
                            "to_block": to_block,
                            "chain_id": chain_id,
                            "contract_address": contract_address,
                            "project_id": project.id,
                        },
                        countdown=1,
                    )

                    last_checked_block = to_block
                    await launchpad_multichain_events_cache.set_last_checked_block(
                        chain_id, contract_address, to_block
                    )
                    await asyncio.sleep(0.5)

        return CommandResult(success=True, need_retry=False)
