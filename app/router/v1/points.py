from typing import Annotated

from fastapi import APIRouter, Body, Header, HTTPException, Path
from sqlalchemy.exc import NoResultFound
from starlette.status import HTTP_403_FORBIDDEN

from app.dependencies import (
    AddPointsDep,
    LaunchpadProjectCrudDep,
    ProfileCrudDep,
    ExtraPointsCrudDep,
)
from app.env import settings
from app.schema import (
    AddPointsRequest,
    AddPointsResponse,
    AddPointsOperationData,
    GetPointsResponse,
    ErrorResponse,
    GetPointsData,
)
from app.utils import check_password

router = APIRouter(prefix="/points", tags=["points"])


@router.post("/add", include_in_schema=False, response_model=AddPointsResponse)
async def add_points(
    service: AddPointsDep,
    projects_crud: LaunchpadProjectCrudDep,
    x_sender_name: Annotated[str, Header()],
    x_sender_token: Annotated[str, Header()],
    request: AddPointsRequest = Body(embed=False),
):
    if (sender := await projects_crud.find_by_id_or_slug(x_sender_name)) is None:
        return AddPointsResponse(ok=False, error="Not authorized")

    if (access_token := sender.access_token) is None or not check_password(
        x_sender_token, access_token.token
    ):
        return AddPointsResponse(ok=False, error="Not authorized")

    operations_results = []
    for operation in request.operations:
        try:
            project_id = None
            if operation.project_slug:
                if (
                    project := await projects_crud.find_by_id_or_slug(operation.project_slug)
                ) is None:
                    raise NoResultFound("Project not found")

                if sender.slug not in [project.slug, settings.admin_project_name]:
                    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")

                project_id = project.id

            await service.add_points(
                address=operation.address,
                amount=operation.amount,
                operation_type=operation.operation_type,
                project_id=project_id,
                operation_reason=operation.operation_reason,
            )
            operations_results.append(AddPointsOperationData(address=operation.address, ok=True))
        except Exception as e:
            operations_results.append(
                AddPointsOperationData(
                    address=operation.address,
                    ok=False,
                    error=f"Failed to add points: {e}",
                )
            )

    return AddPointsResponse(ok=True, data=operations_results)


@router.get("{id_or_slug}/{address}", response_model=GetPointsResponse | ErrorResponse)
async def get_profile_points(
    projects_crud: LaunchpadProjectCrudDep,
    profiles_crud: ProfileCrudDep,
    extra_points_crud: ExtraPointsCrudDep,
    x_sender_name: Annotated[str, Header()],
    x_sender_token: Annotated[str, Header()],
    id_or_slug: str | int = Path(),
    address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
):
    if (sender := await projects_crud.find_by_id_or_slug(x_sender_name)) is None:
        return ErrorResponse(ok=False, error="Not authorized")

    if sender.slug != settings.admin_project_name:
        return ErrorResponse(ok=False, error="Not authorized")

    if (access_token := sender.access_token) is None or not check_password(
        x_sender_token, access_token.token
    ):
        return ErrorResponse(ok=False, error="Not authorized")

    profile = await profiles_crud.first_by_address(address)
    if profile is None:
        return ErrorResponse(ok=False, error="Profile not found")

    if (project := await projects_crud.find_by_id_or_slug(id_or_slug)) is None:
        return ErrorResponse(ok=False, error="Project not found")

    extra_points = await extra_points_crud.get(profile_id=profile.id, project_id=project.id)
    extra_points = None if extra_points is None else extra_points.points

    return GetPointsResponse(
        ok=True,
        data=GetPointsData(
            points=profile.points, ref_points=profile.ref_points, extra_points=extra_points
        ),
    )
