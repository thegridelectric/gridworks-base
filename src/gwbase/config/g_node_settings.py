"""Settings for the GNodeFactory, readable from environment and/or from env files."""

import datetime

from pydantic import SecretStr
from pydantic import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Self

from gwbase.config.algo_settings import AlgoApiSecrets
from gwbase.config.algo_settings import Public
from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.config.utils import check_g_node_alias
from gwbase.config.utils import check_is_algo_secret_key_format
from gwbase.config.utils import check_is_reasonable_unix_time_s
from gwbase.enums import GNodeRole
from gwbase.enums import UniverseType


DEFAULT_ENV_FILE = ".env"


class GNodeSettings(BaseSettings):
    """
    Template settings for a GNode.
    """

    rabbit: RabbitBrokerClient = RabbitBrokerClient()
    g_node_alias: str = "d1.isone.unknown.gnode"
    g_node_id: str = "e23eb2ec-4064-4921-89d4-b006edc81216"
    g_node_instance_id: str = "00000000-0000-0000-0000-000000000000"
    my_super_alias: str = "d1.super1"
    g_node_role_value: str = "GNode"
    sk: SecretStr = SecretStr(
        "3g+IYDCVM84Ady7a8fGImRkEZ77+a4e3i14ub0QMjM/JKlzB2GNdv0S+lqMsYgPiGbd7aAp5943X5NzvdQJohw=="
    )
    # Secret key for public Algorand adress ZEVFZQOYMNO36RF6S2RSYYQD4IM3O63IBJ47PDOX4TOO65ICNCDUF4HMLE
    universe_type_value: str = "Dev"
    my_time_coordinator_alias: str = "d1.time"
    initial_time_unix_s: int = int(
        datetime.datetime(2020, 1, 1, 4, 20, tzinfo=datetime.timezone.utc).timestamp()
    )

    log_level: str = "INFO"
    public: Public = Public()
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    redis_endpoint: str = "localhost"
    minute_cron_file: str = "cron_last_minute.txt"
    hour_cron_file: str = "cron_last_hour.txt"
    day_cron_file: str = "cron_last_day.txt"

    @field_validator("initial_time_unix_s", mode="before")
    def convert_initial_time_unix_s(cls, value):
        return int(value)

    @model_validator(mode="after")
    def validate_setting_axioms(self) -> Self:
        """
        Validates the following:
            - universe_type_value belongs to the GridWorks UniverseType enum
            - g_node_role_value belongs to the GridWOrks GNodeRole enum
            - All GNodeAliases (self, my time coordinator, my super) have the correct
            LeftRightDot format and match the alias pattern for the universe type
            - sk.get_secret_value() has the format of an Algorand secret key
            - initial_time_unix_s is a reasonable unix time in ms
        """
        if self.universe_type_value not in UniverseType.values():
            raise ValueError("universe_type_value must belong to UniverseType.values()")
        universe_type = UniverseType(self.universe_type_value)
        if self.g_node_role_value not in GNodeRole.values():
            raise ValueError("g_node_role_value must belong to GNodeRole.values()")
        check_g_node_alias(alias=self.g_node_alias, universe_type=universe_type)
        check_g_node_alias(
            alias=self.my_time_coordinator_alias, universe_type=universe_type
        )
        check_g_node_alias(alias=self.my_super_alias, universe_type=universe_type)
        check_is_algo_secret_key_format(self.sk.get_secret_value())
        check_is_reasonable_unix_time_s(self.initial_time_unix_s)
        return self

    class Config:
        env_prefix = "GNODE_"
        env_nested_delimiter = "__"


class SupervisorSettings(BaseSettings):
    g_node_alias: str = "d1.isone.ver.keene.super1"
    g_node_id: str = "664a3250-ce51-4fe3-9ce9-a4b6416451fb"
    g_node_instance_id: str = "20e7edec-05e5-4152-bfec-ec21ddd2e3dd"
    supervisor_container_id: str = "995b0334-9940-424f-8fb1-4745e52ba295"
    g_node_role_value: str = "Supervisor"
    my_time_coordinator_alias: str = "d1.time"
    log_level: str = "INFO"
    universe_type_value: str = "Dev"
    world_instance_name: str = "d1__1"
    rabbit: RabbitBrokerClient = RabbitBrokerClient()

    class Config:
        env_prefix = "SUPER_"
        env_nested_delimiter = "__"