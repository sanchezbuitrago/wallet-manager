import asyncio

from app.commons import event_bus as eb
from app.commons import logs
from app.commons.adapters import mongo_uow
from app.commons.adapters import outbox

_LOGGER = logs.get_logger()


class OutboxWorker:
    """Background worker that polls the outbox and publishes events.

    Runs as an asyncio task, checking for unpublished events at a
    configurable interval and dispatching them through the EventBus.
    """

    def __init__(self, interval: float = 5.0):
        self._interval = interval
        self._running = False

    async def start(self) -> None:
        """Start the polling loop."""
        self._running = True
        _LOGGER.info("Outbox worker started (interval=%ss)", self._interval)
        while self._running:
            await self._process_pending()
            await asyncio.sleep(self._interval)

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False

    async def _process_pending(self) -> None:
        try:
            uow = mongo_uow.MongoUOW()
            outbox_repo = uow.get_repo(outbox.OutboxEvent)
            pending = list(outbox_repo.find_by(
                find={"published": False},
                sort_by="created_at",
                descending=False
            ))

            _LOGGER.info("Processing [%s] pending events", len(pending))

            for outbox_event in pending:
                try:
                    event_class = eb.find_event_class(outbox_event.event_type)
                    if not event_class:
                        _LOGGER.error(
                            "Event class not found: %s",
                            outbox_event.event_type
                        )
                        continue

                    event = event_class(**outbox_event.payload)
                    await eb.event_bus.publish(event)

                    outbox_event.mark_published()
                    outbox_repo.save(outbox_event)
                    _LOGGER.info(
                        "Published event %s [%s]",
                        outbox_event.event_type,
                        outbox_event.id.key()
                    )
                except Exception as e:
                    _LOGGER.error(
                        "Failed to publish event %s: %s",
                        outbox_event.event_type,
                        e
                    )
        except Exception as e:
            _LOGGER.error("Outbox worker error: %s", e)
