from typing import Annotated

from fastapi import APIRouter, Body, Header, HTTPException
from sqlalchemy.exc import NoResultFound
from starlette.status import HTTP_403_FORBIDDEN

from app.dependencies import AddPointsDep, LaunchpadProjectCrudDep
from app.env import settings
from app.schema import AddPointsRequest, AddPointsResponse, AddPointsOperationData
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
                operation.address,
                operation.amount,
                operation.operation_type,
                project_id,
                operation.operation_reason,
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
