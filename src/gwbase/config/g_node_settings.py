from pathlib import Path

from pydantic import Field

from gwbase.config.paths import g_node_gt_path
from gwbase.config.service_settings import ServiceSettings


class GNodeSettings(ServiceSettings):
    """``ServiceSettings`` + GNode-only durable identity.

    The durable identity (``GNodeId``, free-form ``GNodeClass``, and the
    binding ``Alias``) is provisioned on disk as a ``g.node.gt.json`` file at
    ``g_node_path`` and loaded + Sema-validated by ``GridworksActor`` at
    construction (see ``gridworks_actor.py``). Used by ``GridworksActor``.

    No ``transport_class`` here — it is intrinsic to the actor's role, not
    deployment config, and is supplied as an ``Orchestrator`` ``__init__``
    param. Inherits the ``GWBASE_`` env prefix from ``ServiceSettings``.
    """

    g_node_path: Path = Field(
        default_factory=lambda data: g_node_gt_path(data["service_name"]),
    )
    # gnr's public façade, e.g. "https://gnr.electricity.works". Lets the
    # actor re-read its alias by GNodeId before every reconnect, so a
    # registry rename converges without a provisioning redeploy. None turns
    # that off (a dev rung with no gnr), and the actor says so at boot.
    gnr_url: str | None = None
    gnr_timeout_s: float = 5.0
