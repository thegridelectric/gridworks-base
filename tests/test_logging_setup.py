"""The log timestamp: RFC 3339 with millis and the numeric offset of
``log_tz``, so the fall-back hour reads as two different instants."""

import logging
from zoneinfo import ZoneInfo

from gwbase.logging_setup import HumanFormatter, iso_timestamp

# 2026-11-06T21:37:56.795Z: the flo answered oak at 16:37 Eastern.
OAK_ANSWER = 1794001076.795
# 2026-11-01 in Maine: the clocks fell back at 02:00 EDT -> 01:00 EST.
# 05:30Z is 01:30 EDT; one hour later 06:30Z is 01:30 EST.
FALL_BACK_EDT = 1793511000.0
FALL_BACK_EST = FALL_BACK_EDT + 3600

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


def test_iso_renders_in_zone_with_offset() -> None:
    assert iso_timestamp(OAK_ANSWER, ET) == "2026-11-06T16:37:56.795-05:00"
    assert iso_timestamp(OAK_ANSWER, UTC) == "2026-11-06T21:37:56.795+00:00"


def test_iso_fall_back_hour_names_one_instant() -> None:
    edt = iso_timestamp(FALL_BACK_EDT, ET)
    est = iso_timestamp(FALL_BACK_EST, ET)
    assert edt == "2026-11-01T01:30:00.000-04:00"
    assert est == "2026-11-01T01:30:00.000-05:00"
    assert edt != est


def test_formatter_line_uses_zone() -> None:
    record = logging.makeLogRecord({
        "msg": "Answered %s in %.1f s",
        "args": ("hw1.isone.me.versant.keene.oak", 6.5),
        "levelname": "INFO",
        "created": OAK_ANSWER,
        "service_alias": "hw1.flo",
    })
    line = HumanFormatter(ET).format(record)
    assert line.startswith("2026-11-06T16:37:56.795-05:00 INFO  hw1.flo > Answered")
