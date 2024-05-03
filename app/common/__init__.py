import asyncio
import inspect
from abc import abstractmethod
from contextlib import AsyncExitStack

from fastapi import Request
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import solve_dependencies, get_dependant
from pydantic import ValidationError


class CommandResult:
    def __init__(self, success: bool, need_retry: bool = False, retry_after: int = 5):
        self.success = success
        self.need_retry = need_retry
        self.retry_after = retry_after


class Command:
    @abstractmethod
    async def command(self) -> CommandResult:
        pass

    @staticmethod
    async def _execute_command(request: Request, dependant: Dependant):
        async with AsyncExitStack() as async_exit_stack:
            values, errors, _1, _2, _3 = await solve_dependencies(
                request=request, dependant=dependant, async_exit_stack=async_exit_stack
            )
            if errors:
                raise ValidationError(errors, None)
            if inspect.iscoroutinefunction(dependant.call):
                result = await dependant.call(**values)
            else:
                result = dependant.call(**values)

            return result

    async def run(self):
        async with AsyncExitStack() as cm:
            request = Request(
                {
                    "type": "http",
                    "headers": [],
                    "query_string": "",
                    "fastapi_astack": cm,
                }
            )
            dependant = get_dependant(path=f"command:{self.__class__.__name__}", call=self.command)
            return await self._execute_command(request, dependant)


def run_command_and_get_result(command: Command) -> CommandResult:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(command.run())

    return result
