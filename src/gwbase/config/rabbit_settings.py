from pydantic import BaseModel
from pydantic import SecretStr


class RabbitBrokerClient(BaseModel):
    """Settings for connecting to a Rabbit Broker"""

    url: SecretStr = SecretStr("amqp://smqPublic:smqPublic@localhost:5672/d1__1")
