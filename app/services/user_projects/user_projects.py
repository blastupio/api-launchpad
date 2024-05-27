from sqlalchemy import Sequence, Row

from app.services.user_projects.multicall import get_projects_ids_of_user


async def get_user_registered_projects(
    projects_crud, user_address: str, page: int, size: int
) -> tuple[Sequence[Row], int]:
    contract_project_ids = await projects_crud.get_contract_project_ids()
    projects_ids_of_user = await get_projects_ids_of_user(user_address, contract_project_ids)
    projects = await projects_crud.get_projects_by_contract_project_ids(
        projects_ids_of_user, page, size
    )
    return projects, len(projects_ids_of_user)
