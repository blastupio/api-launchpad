import argparse
import asyncio
import logging
import sys

import sentry_sdk

from app.env import settings
from app.services.analytics.jobs import ProcessLaunchpadContractEvents
from app.services.stake_history.jobs import ProcessHistoryStakingEvent
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
        "monitor-onramp-balance",
        "update-project-total-raised",
        "process-launchpad-contract-events",
    ]:
        subparsers.add_parser(command)

    args = parser.parse_args()
    match args.command:
        case "listen-staking-events":
            command = ProcessHistoryStakingEvent()
        case "monitor-onramp-balance":
            command = MonitorSenderBalance()
        case "update-project-total-raised":
            command = RecalculateProjectsTotalRaised()
        case "process-launchpad-contract-events":
            command = ProcessLaunchpadContractEvents()
        case _:
            command = None

    if command is None:
        raise Exception("This code should not be reached!")

    result = await command.run_async()

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
