from sqlalchemy.dialects.postgresql import insert

from app.base import BaseCrud
from app.models import LaunchpadContractEvents
from app.schema import CreateLaunchpadEvent


class LaunchpadContractEventsCrud(BaseCrud):
    async def add_event(self, params: CreateLaunchpadEvent):
        values = params.dict()
        values["user_address"] = values["user_address"].lower()
        values["token_address"] = values["token_address"].lower()
        st = (
            insert(LaunchpadContractEvents)
            .values(values)
            .on_conflict_do_nothing(constraint="ux_launchpad_contract_events_txn_hash")
        )
        await self.session.execute(st)
