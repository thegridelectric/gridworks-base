"""Read a GNode's current registry record from gnr over its public façade."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import GNodeGt

LOGGER = logging.getLogger(__name__)


def get_g_node_by_id(gnr_url: str, g_node_id: str, timeout_s: float) -> GNodeGt | None:
    """``GET <gnr_url>/gnr/g-node-by-id/<g_node_id>`` decoded as a ``GNodeGt``.

    ``None`` when gnr is unreachable, answers 404, or answers something that
    is not a ``GNodeGt``; each case is logged, and the caller keeps what it
    already holds.
    """
    url = f"{gnr_url.rstrip('/')}/gnr/g-node-by-id/{g_node_id}"
    try:
        with urlopen(url, timeout=timeout_s) as resp:  # noqa: S310 (operator-configured gnr URL)
            data = json.load(resp)
    except HTTPError as e:
        LOGGER.warning("gnr %s answered %s", url, e.code)
        return None
    except (URLError, TimeoutError, OSError) as e:
        LOGGER.warning("gnr %s unreachable: %s", url, e)
        return None
    try:
        return GwBaseSemaCodec().from_dict(data, expect=GNodeGt)
    except ValueError as e:
        LOGGER.warning("gnr %s answered something that is not a GNodeGt: %s", url, e)
        return None
