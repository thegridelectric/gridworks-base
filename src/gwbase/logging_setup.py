"""Per-actor logging substrate for ``ActorBase``.

Builds a contextualized ``logging.Logger`` at actor construction that writes
a **bijective human-readable** format to an XDG state-home log file. The
format maps 1:1 onto a future ``observability.log-entry/000`` Sema type, so a
downstream broker-forwarding handler can attach to the same logger without
any actor-side code change.

Per-record line:  ``<iso-ts> <LEVEL> <alias> > <message>[ key=val ...]``
Exception info follows as ``  | ...`` continuation lines. The timestamp is
RFC 3339 with milliseconds in the service's ``log_tz`` and always ends in
the numeric UTC offset (``2026-11-06T16:37:56.795-05:00``), so a line
reads in the hour the operator lives in and still names one instant:
the DST fall-back hour does not repeat, and logs from boxes in different
zones sort and correlate.

The downstream observability work (BrokerLoggingHandler, verbosity-request)
is intentionally NOT built here — this is substrate only.
"""

import logging
import logging.handlers
from datetime import datetime
from zoneinfo import ZoneInfo

from gwbase.config import paths

# Slots the formatter reads from each record; injected by _ContextFilter.
_CTX_ALIAS = "service_alias"
_CTX_INSTANCE = "instance_id"

# Reserved LogRecord attributes — anything else passed via `extra=` becomes a
# trailing `key=val` token (bijective to the Sema `Extra` dict).
_RESERVED_RECORD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__.keys()) | {
    _CTX_ALIAS,
    _CTX_INSTANCE,
    "message",
    "asctime",
    "taskName",
}


def iso_timestamp(epoch_s: float, tz: ZoneInfo) -> str:
    """epoch seconds -> RFC 3339 with millis and numeric offset in ``tz``,
    e.g. ``2026-11-06T16:37:56.795-05:00`` (``+00:00`` for UTC)."""
    return datetime.fromtimestamp(epoch_s, tz=tz).isoformat(timespec="milliseconds")


class _ContextFilter(logging.Filter):
    """Inject service_alias + instance_id onto every record."""

    def __init__(self, service_alias: str, instance_id: str) -> None:
        super().__init__()
        self._service_alias = service_alias
        self._instance_id = instance_id

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, _CTX_ALIAS, self._service_alias)
        setattr(record, _CTX_INSTANCE, self._instance_id)
        return True


class HumanFormatter(logging.Formatter):
    """The bijective human format (the only Wave-1 format); timestamps in ``tz``."""

    def __init__(self, tz: ZoneInfo) -> None:
        super().__init__()
        self.tz = tz

    def format(self, record: logging.LogRecord) -> str:
        alias = getattr(record, _CTX_ALIAS, "-")
        line = (
            f"{iso_timestamp(record.created, self.tz)} {record.levelname:<5} "
            f"{alias} > {record.getMessage()}"
        )
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _RESERVED_RECORD_ATTRS and not k.startswith("_")
        }
        if extras:
            line += " " + " ".join(f"{k}={v}" for k, v in extras.items())
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            line += "\n" + "\n".join(f"  | {ln}" for ln in exc_text.splitlines())
        return line


def _build_actor_logger(  # noqa: PLR0913 — logger builder fans out logging settings
    *,
    service_name: str,
    service_alias: str,
    instance_id: str,
    log_level: str,
    log_tz: str,
    rotate_bytes: int,
    rotate_count: int,
) -> logging.Logger:
    """Build the per-actor logger (named ``gwbase.actor.<service_alias>``)
    with a RotatingFileHandler to ``log_dir(service_name)/<alias>.log``, the
    context filter, and the bijective human formatter. Idempotent per alias."""
    paths.mkdirs(service_name)

    logger = logging.getLogger(f"gwbase.actor.{service_alias}")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.propagate = False  # the file (and future broker handler) is the sink
    logger.handlers.clear()  # idempotent if re-built for the same alias

    handler = logging.handlers.RotatingFileHandler(
        paths.log_dir(service_name) / f"{service_alias}.log",
        maxBytes=rotate_bytes,
        backupCount=rotate_count,
    )
    tz = ZoneInfo(log_tz)
    handler.setFormatter(HumanFormatter(tz))
    handler.addFilter(_ContextFilter(service_alias, instance_id))
    logger.addHandler(handler)

    # File header (bijective: alias -> Alias, instance -> InstanceId).
    # RotatingFileHandler opens its stream at construction (delay=False,
    # the default), so it is never None here; the annotation is Optional
    # only for delay=True handlers.
    assert handler.stream is not None
    handler.stream.write(
        f"=== gwbase log: alias={service_alias} instance={instance_id} "
        f"started={iso_timestamp(datetime.now(tz=tz).timestamp(), tz)} ===\n"
    )
    handler.flush()

    return logger
