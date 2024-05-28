import asyncio

from httpx import AsyncClient
from sqlalchemy import Sequence, Row

from app.base import logger
from app.dependencies import LaunchpadProjectCrudDep
from app.models import ProjectType
from app.services.user_projects.multicall import get_projects_ids_of_user


async def get_multichain_project_ids_of_user(
    user_address: str, proxy_url_by_project_id: dict[str, str]
) -> list[str]:
    async def get_user_registered(proxy_url: str) -> bool:
        _url = f"{proxy_url.rstrip('/')}/"
        url = f"{_url}users/profile/{user_address}/transactions?limit=1&offset=0"
        async with AsyncClient(timeout=10) as client:
            err = None
            for _ in range(5):
                try:
                    response = await client.get(url)
                    json_response = response.json()
                    return json_response["count"] > 0
                except Exception as e:
                    err = e
            if err:
                logger.error(f"Can't get transactions count for {user_address=}: {err}")
            return False

    tasks = [get_user_registered(proxy_url) for proxy_url in proxy_url_by_project_id.values()]
    results = await asyncio.gather(*tasks)
    return [
        proj_id
        for (proj_id, registered) in zip(proxy_url_by_project_id.keys(), results)
        if registered
    ]


async def get_user_registered_projects(
    projects_crud: LaunchpadProjectCrudDep, user_address: str, page: int, size: int
) -> tuple[Sequence[Row], int]:
    info = await projects_crud.get_info_for_user_projects()

    # get private multichain projects ids of user from proxy_url
    proxy_url_by_project_id = {
        x.id: x.base_url for x in info if x.project_type == ProjectType.PRIVATE_PRESALE
    }
    multichain_project_ids_of_user = await get_multichain_project_ids_of_user(
        user_address, proxy_url_by_project_id
    )

    # get default projects ids of user
    contract_project_id_by_project_id = {
        x.id: x.contract_project_id
        for x in info
        if x.project_type == ProjectType.DEFAULT and x.contract_project_id is not None
    }
    try:
        # try to get via blockchain method users
        default_projects_ids_of_user = await get_projects_ids_of_user(
            user_address, contract_project_id_by_project_id
        )
        total_default_projects = len(default_projects_ids_of_user)
    except Exception as e:
        logger.error(f"Cannot get user projects for {user_address} via blockchain: {e}")
        # get via launchpad events from db
        default_projects_ids_of_user, total_default_projects = (
            await projects_crud.get_user_project_ids_from_events(user_address, page, size)
        )

    total_projects = len(multichain_project_ids_of_user) + total_default_projects
    projects = await projects_crud.get_projects_by_ids(
        project_ids=default_projects_ids_of_user + multichain_project_ids_of_user,
        page=page,
        size=size,
    )
    return projects, total_projects
