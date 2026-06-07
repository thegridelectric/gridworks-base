"""Per-actor logging substrate for ``ActorBase``.

Builds a contextualized ``logging.Logger`` at actor construction that writes
a **bijective human-readable** format to an XDG state-home log file. The
format maps 1:1 onto a future ``observability.log-entry/000`` Sema type, so a
downstream broker-forwarding handler can attach to the same logger without
any actor-side code change.

Per-record line:  ``<iso-ts> <LEVEL> <alias> > <message>[ key=val ...]``
Exception info follows as ``  | ...`` continuation lines.

Spec: ``wiki/gridworks-base/designs/support-non-gnode-actors/logging.md``.
The downstream observability work (BrokerLoggingHandler, verbosity-request)
lives in ``wiki/gridworks-base/research/concerns/logging-for-observability.md``
and is intentionally NOT built here — this is substrate only.
"""

import logging
import logging.handlers
from datetime import UTC, datetime

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


def _iso(epoch_s: float) -> str:
    """epoch seconds -> 'YYYY-MM-DDTHH:MM:SS.mmmZ' (millis, UTC)."""
    return (
        datetime.fromtimestamp(epoch_s, tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        + "Z"
    )


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


class _HumanFormatter(logging.Formatter):
    """The bijective human format (the only Wave-1 format)."""

    def format(self, record: logging.LogRecord) -> str:
        alias = getattr(record, _CTX_ALIAS, "-")
        line = (
            f"{_iso(record.created)} {record.levelname:<5} "
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
    handler.setFormatter(_HumanFormatter())
    handler.addFilter(_ContextFilter(service_alias, instance_id))
    logger.addHandler(handler)

    # File header (bijective: alias -> Alias, instance -> InstanceId).
    handler.stream.write(
        f"=== gwbase log: alias={service_alias} instance={instance_id} "
        f"started={_iso(datetime.now(tz=UTC).timestamp())} ===\n"
    )
    handler.flush()

    return logger
