import traceback

from celery import Celery
from celery.exceptions import Retry

from app.base import logger
from app.common import run_command_and_get_result
from app.env import settings
from onramp.jobs import ProcessMunzenOrder

app = Celery("tasks", broker=settings.celery_broker)


@app.task(
    max_retries=10,
    default_retry_delay=15,
)
def process_munzen_order(entity_id: str):
    try:
        result = run_command_and_get_result(ProcessMunzenOrder(entity_id))

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            process_munzen_order.apply_async(args=[entity_id], countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"process_munzen_order[{entity_id}] Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)
