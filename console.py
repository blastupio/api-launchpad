import argparse
import asyncio
import logging
import sys

import sentry_sdk

from app.env import settings
from app.services.launchpad.jobs import ProcessLaunchpadContractEvents
from app.services.blp_staking.jobs import ProcessBlpHistoryStakingEvent, AddBlpStakingPoints
from app.services.prices.jobs import UpdateSupportedTokensCache
from app.services.ido_staking.jobs import ProcessHistoryStakingEvent, AddIdoStakingPoints
from app.services.projects.jobs import ChangeProjectsStatus
from app.services.total_raised.jobs import RecalculateProjectsTotalRaised
from onramp.jobs import MonitorSenderBalance

if settings.sentry_dsn is not None:
    sentry_sdk.init(dsn=settings.sentry_dsn, enable_tracing=True)

logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(prog="console.py", description="Launchpad console runner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    for command in [
        "listen-staking-events",
        "listen-blp-staking-events",
        "monitor-onramp-balance",
        "update-project-total-raised",
        "process-launchpad-contract-events",
        "update-supported-tokens-cache",
        "change-projects-status",
        "add-ido-staking-points",
        "add-blp-staking-points",
    ]:
        subparsers.add_parser(command)

    args = parser.parse_args()
    match args.command:
        case "listen-staking-events":
            command = ProcessHistoryStakingEvent()
        case "listen-blp-staking-events":
            command = ProcessBlpHistoryStakingEvent()
        case "monitor-onramp-balance":
            command = MonitorSenderBalance()
        case "update-project-total-raised":
            command = RecalculateProjectsTotalRaised()
        case "process-launchpad-contract-events":
            command = ProcessLaunchpadContractEvents()
        case "update-supported-tokens-cache":
            command = UpdateSupportedTokensCache()
        case "add-ido-staking-points":
            command = AddIdoStakingPoints()
        case "add-blp-staking-points":
            command = AddBlpStakingPoints()
        case "change-projects-status":
            command = ChangeProjectsStatus()
        case _:
            command = None

    if command is None:
        raise Exception("This code should not be reached!")

    result = await command.run_async()

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
