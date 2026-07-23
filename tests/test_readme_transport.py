"""The README's routing-class table is enforced against the code."""

import re
from pathlib import Path

from gwbase.transport_encoding import RoutingClass

README = Path(__file__).parent.parent / "README.md"

# Rows shaped: | `ltn` | LeafTransactiveNode |
_ROW = re.compile(r"^\| `([a-z]+)` \| (\w+) \|$", flags=re.MULTILINE)


def test_readme_routing_class_table_matches_enum() -> None:
    rows = dict(_ROW.findall(README.read_text()))
    assert rows == {rc.value: rc.name for rc in RoutingClass}, (
        "README routing-class table has drifted from RoutingClass "
        "(src/gwbase/transport_encoding.py) — update the table."
    )
