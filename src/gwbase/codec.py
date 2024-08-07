import json

from gw.errors import GwTypeError

from gwbase.types.asl_types import TypeMakerByName
from gwbase.types.heartbeat_a import HeartbeatA

type_list = list(TypeMakerByName.keys())


def deserializer(msg_bytes: bytes) -> HeartbeatA:
    """
    Given an instance of the type (i.e., a serialized byte string for sending
    as a message), returns the appropriate instance of the associated pydantic
    BaseModel class.

    Raises: GwTypeError if msg_bytes fails the type authentication
    """
    content = json.loads(msg_bytes.decode("utf-8"))
    if "TypeName" not in content.keys():
        raise GwTypeError(f"No TypeName - so not a type. Keys: <{content.keys()}>")
    outer_type_name = content["TypeName"]

    # Andrew puts all his messages in a wrapper of tn 'gw'
    # which must have a 'Payload'.
    if outer_type_name == "gw":
        if "Payload" not in content.keys():
            raise GwTypeError(f"Type Gw must include Payload! Keys: <{content.keys()}>")
        content = content["Payload"]

    Codec = TypeMakerByName[content["TypeName"]]
    return Codec.dict_to_tuple(content)


def serializer(t: HeartbeatA) -> bytes:
    """
    Given an instance of a pydantic BaseModel class associated to a type,
    returns the approriate instance of the serialized type.

    Raises: GwTypeError if t fails authentication

    """
    return t.as_type()
