from gw.enums import MessageCategory
from gw_test import wait_for

from gwbase.actor_base import ActorBase
from gwbase.config import GNodeSettings
from gwbase.types import HeartbeatA


class HelloGNode(ActorBase):
    def __init__(self, settings: GNodeSettings):
        super().__init__(settings=settings)
        self.settings: GNodeSettings = settings

    def prepare_for_death(self) -> None:
        self._main_loop_running = False


def test_hello():
    settings = GNodeSettings()

    settings.g_node_alias = "d1.hello"
    settings.g_node_role_value = "GNode"

    gn = HelloGNode(settings=settings)
    gn.start()
    wait_for(lambda: gn._consuming, 4, "gnode is consuming")
    hb = HeartbeatA(my_hex="a", your_last_hex="0")
    gn.send_message(payload=hb, message_category=MessageCategory.RabbitJsonBroadcast)

    gn.stop()
