from gw.enums import MessageCategory
from gwbase.actor_base import ActorBase
from gwbase.config import GNodeSettings
from gwbase.enums import GNodeRole
from gwbase.types import HeartbeatA


class HelloGNode(ActorBase):
    def __init__(self, settings: GNodeSettings):
        super().__init__(settings=settings)
        self.settings: GNodeSettings = settings


def demo():
    input(
        "Go to http://0.0.0.0:15672/#/queues/d1__1/dummy_ear_q and purge the messages from the dummy ear queue",
    )
    settings = GNodeSettings()

    settings.g_node_alias = "d1.hello"
    settings.g_node_role_value = "GNode"

    gn = HelloGNode(settings=settings)
    gn.start()

    input(
        "Go to http://0.0.0.0:15672/#/queues and wait for the d1.hello-Fxxxx queue to appear.",
    )
    assert gn.g_node_role == GNodeRole.GNode
    hb = HeartbeatA(my_hex=0, your_last_hex="a")

    print("Broadcasting a heartbeat on rabbitmq")
    print(hb.as_type())
    gn.send_message(payload=hb, message_category=MessageCategory.RabbitJsonBroadcast)

    print("Inspect the dummy ear queue to examine the message (click on GetMessage)")
    input("http://0.0.0.0:15672/#/queues/d1__1/dummy_ear_q")
    input("Hit return to tear down the GNode rabbit actor")
    gn.stop()
    input("Verify that d1.hello-Fxxx is gone from the rabbit queue")


if __name__ == "__main__":
    demo()
