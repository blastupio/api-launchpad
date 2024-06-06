from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.points import PointsHistoryCrud, ExtraPointsCrud
from app.crud.profiles import ProfilesCrud
from app.models import Profile, PointsHistory, OperationType, OperationReason


class AddPoints:
    def __init__(
        self,
        profile_crud: ProfilesCrud,
        points_history_crud: PointsHistoryCrud,
        extra_points_crud: ExtraPointsCrud,
    ):
        self.profile_crud = profile_crud
        self.points_history_crud = points_history_crud
        self.extra_points_crud = extra_points_crud

    async def add_points(
        self,
        address: str,
        amount: int,
        operation_type: OperationType,
        project_id: str | None = None,
        referring_profile_id: int | None = None,
        operation_reason: OperationReason | None = None,
        session: AsyncSession | None = None,
    ) -> Profile:
        profile = await self.profile_crud.first_by_address_or_fail_with_lock(address, session)

        extra_amount = 0
        if project_id is not None:
            extra_amount = amount

        points_before = profile.points
        profile.points += amount
        if operation_type == OperationType.ADD_REF:
            profile.ref_points += amount

        await self.profile_crud.persist(profile, session)

        history = PointsHistory(
            profile_id=profile.id,
            points_before=points_before,
            amount=amount,
            points_after=profile.points,
            operation_type=operation_type,
            operation_reason=operation_reason,
            referring_profile_id=referring_profile_id,
        )
        await self.points_history_crud.persist(history, session)

        if extra_amount > 0:
            points_before = profile.points
            profile.points += extra_amount
            await self.profile_crud.persist(profile, session)

            history = PointsHistory(
                profile_id=profile.id,
                points_before=points_before,
                amount=extra_amount,
                points_after=profile.points,
                operation_type=OperationType.ADD_EXTRA,
                project_id=project_id,
                operation_reason=operation_reason,
            )
            await self.points_history_crud.persist(history, session)

            extra_points = await self.extra_points_crud.get_or_create_with_lock(
                profile.id, project_id, session
            )
            extra_points.points += extra_amount
            await self.extra_points_crud.persist(extra_points, session)

        return profile
