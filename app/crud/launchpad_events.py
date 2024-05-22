from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from app.base import BaseCrud
from app.models import LaunchpadContractEvents
from app.schema import CreateLaunchpadEvent


class LaunchpadContractEventsCrud(BaseCrud):
    async def get_all_events(self, conn: AsyncConnection):
        st = select(LaunchpadContractEvents).order_by(LaunchpadContractEvents.created_at.desc())
        result = (await conn.execute(st)).all()
        return result

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

    async def get_tier_by_user_address_and_contract_project_id(
        self, conn: AsyncConnection
    ) -> dict[str, int]:
        query = """
        SELECT JSON_OBJECT_AGG(
          user_address || '_' || contract_project_id,
          (extra ->> 'tier')::int
        ) AS result
        FROM launchpad_contract_events
        WHERE event_type = 'USER_REGISTERED'
        """
        res = (await conn.execute(text(query))).scalar_one_or_none()
        return res or {}
