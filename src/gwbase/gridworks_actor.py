import json
import logging
from abc import ABC

from gwbase.config import GNodeSettings
from gwbase.orchestrator import Orchestrator
from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import GNodeGt
from gwbase.transport_encoding import TransportClass

LOGGER = logging.getLogger(__name__)


class GridworksActor(Orchestrator, ABC):
    """An ``Orchestrator`` that carries durable GNode identity.

    The identity is provisioned on disk as a ``g.node.gt.json`` file at
    ``settings.g_node_path`` and is loaded + **Sema-validated** as a real
    ``GNodeGt`` at construction (axioms 1–5 fire), rather than read as three
    untyped strings. A drifted or malformed file fails at boot with a clear
    error instead of a confusing mid-run crash. The binding invariant
    ``GNodeGt.alias == settings.service_alias`` catches provisioning drift
    between the artifact and the runtime config.

    Used by SCADA, LTN, MarketMaker, the forecast services, etc. — one
    subclass per ``TransportClass``, each passing its fixed ``transport_class``
    up to ``Orchestrator``.
    """

    def __init__(
        self,
        *,
        settings: GNodeSettings,
        transport_class: TransportClass,
        my_super_alias: str,
        my_time_coordinator_alias: str,
    ):
        super().__init__(
            settings=settings,
            transport_class=transport_class,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )

        # Load + Sema-validate the GNode identity at the boundary.
        try:
            g_node_data = json.loads(settings.g_node_path.read_text())
        except FileNotFoundError as e:
            raise ValueError(
                f"GridworksActor requires {settings.g_node_path} to exist; "
                f"provision via gridworks-provisioning first"
            ) from e
        except json.JSONDecodeError as e:
            raise ValueError(f"{settings.g_node_path} is not valid JSON: {e}") from e

        try:
            g_node_gt = GwBaseSemaCodec().from_dict(g_node_data, mode="strict")
        except Exception as e:
            raise ValueError(
                f"{settings.g_node_path} failed GNodeGt Sema validation: {e}"
            ) from e

        if not isinstance(g_node_gt, GNodeGt):
            raise ValueError(
                f"{settings.g_node_path} is not a GNodeGt: "
                f"got {type(g_node_gt).__name__}"
            )

        # Binding invariant: provisioning artifact MUST agree with runtime.
        if g_node_gt.alias != settings.service_alias:
            raise ValueError(
                f"Provisioning drift: GNodeGt.alias {g_node_gt.alias!r} in "
                f"{settings.g_node_path} != settings.service_alias "
                f"{settings.service_alias!r} in runtime config"
            )

        self.g_node_id: str = g_node_gt.g_node_id
        self.g_node_class: str = g_node_gt.g_node_class

    # ------------------------------------------------------------------
    # FIS handshake — decorate with the GNodeClass marker
    # ------------------------------------------------------------------

    def _client_properties(self) -> dict:
        """Add ``GNodeClass`` — FIS's discriminator that this connection is a
        GNode — on top of the service-level ServiceAlias/ServiceInstanceId."""

        return {**super()._client_properties(), "GNodeClass": self.g_node_class}

    # ------------------------------------------------------------------
    # Back-compat property aliases (callers used the g_node_* names)
    # ------------------------------------------------------------------

    @property
    def g_node_alias(self) -> str:
        return self.alias

    @property
    def g_node_instance_id(self) -> str:
        return self.instance_id
