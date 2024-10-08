"""
Tests for enum message.category.000 from the GridWorks Type Registry.
"""

from gwbase.enums import MessageCategory


def test_message_category() -> None:
    assert set(MessageCategory.values()) == {
        "Unknown",
        "RabbitJsonDirect",
        "RabbitJsonBroadcast",
        "RabbitGwSerial",
        "MqttJsonBroadcast",
        "RestApiPost",
        "RestApiPostResponse",
        "RestApiGet",
    }

    assert MessageCategory.default() == MessageCategory.Unknown
    assert MessageCategory.enum_name() == "message.category"
    assert MessageCategory.enum_version() == "000"
