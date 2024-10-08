import datetime

import pytest
from gwbase.config import GNodeSettings
from gwbase.config.algo_settings import AlgoApiSecrets, Public
from gwbase.config.rabbit_settings import RabbitBrokerClient
from pydantic import SecretStr

# TODO: implement paths and clean_g_node_env like for scada


def test_g_node_settings_defaults():
    settings = GNodeSettings()
    expected = dict(
        public=Public().model_dump(),
        algo_api_secrets=AlgoApiSecrets().model_dump(),
        rabbit=RabbitBrokerClient().model_dump(),
        redis_endpoint="localhost",
        g_node_alias="d1.isone.unknown.gnode",
        g_node_id="00000000-0000-0000-0000-000000000000",
        g_node_instance_id="00000000-0000-0000-0000-000000000000",
        g_node_role_value="GNode",
        sk=SecretStr(
            "3g+IYDCVM84Ady7a8fGImRkEZ77+a4e3i14ub0QMjM/JKlzB2GNdv0S+lqMsYgPiGbd7aAp5943X5NzvdQJohw==",
        ),
        universe_type_value="Dev",
        my_super_alias="d1.super1",
        my_time_coordinator_alias="d1.time",
        initial_time_unix_s=int(
            datetime.datetime(
                year=2020,
                month=1,
                day=1,
                hour=4,
                minute=20,
                tzinfo=datetime.timezone.utc,
            ).timestamp(),
        ),
        log_level="INFO",
        minute_cron_file="cron_last_minute.txt",
        hour_cron_file="cron_last_hour.txt",
        day_cron_file="cron_last_day.txt",
    )
    assert settings.model_dump() == expected
    assert (
        settings.rabbit.url.get_secret_value()
        == "amqp://smqPublic:smqPublic@localhost:5672/d1__1"
    )


def test_g_node_settings_validations(monkeypatch):
    """
    Tests that validate_settings_axioms catches problems in settings as anticipated
    """
    default = GNodeSettings()

    # universe_type_value belongs to the GridWorks UniverseType enum
    monkeypatch.setenv("GNODE_UNIVERSE_TYPE_VALUE", "mighty")
    with pytest.raises(ValueError):
        GNodeSettings()
    monkeypatch.setenv("GNODE_UNIVERSE_TYPE_VALUE", default.universe_type_value)

    # g_node_role_value belongs to the GridWOrks GNodeRole enum
    monkeypatch.setenv("GNODE_G_NODE_ROLE_VALUE", "vegetable")
    with pytest.raises(ValueError):
        GNodeSettings()
    monkeypatch.setenv("GNODE_G_NODE_ROLE_VALUE", default.g_node_role_value)

    # All GNodeAliases (self, my time coordinator, my super) have the correct
    # LeftRightDot format and match the alias pattern for the universe type
    uc_aliases = ["G_NODE_ALIAS", "MY_SUPER_ALIAS", "MY_TIME_COORDINATOR_ALIAS"]
    for uc_alias in uc_aliases:
        monkeypatch.setenv(f"GNODE_{uc_alias}", "1splat")
        with pytest.raises(ValueError):
            GNodeSettings()
        monkeypatch.setenv(f"GNODE_{uc_alias}", getattr(default, uc_alias.lower()))
        monkeypatch.setenv(f"GNODE_{uc_alias}", "hw1.isone.unknown.gnode")
        with pytest.raises(ValueError):
            GNodeSettings()
        monkeypatch.setenv(f"GNODE_{uc_alias}", getattr(default, uc_alias.lower()))

    # sk.get_secret_value() has the format of an Algorand secret key
    monkeypatch.setenv("GNODE_SK", "not_a_private_algo_key")
    with pytest.raises(ValueError):
        GNodeSettings()
    monkeypatch.setenv("GNODE_SK", default.sk.get_secret_value())

    # initial_time_unix_s is a reasonable unix time in ms
    monkeypatch.setenv("GNODE_INITIAL_TIME_UNIX_S", str(100))
    with pytest.raises(ValueError):
        GNodeSettings()
    monkeypatch.setenv("GNODE_INITIAL_TIME_UNIX_S", str(default.initial_time_unix_s))
    GNodeSettings()
