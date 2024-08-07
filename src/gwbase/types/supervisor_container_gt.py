"""Type supervisor.container.gt, version 000"""

import json
import logging
from typing import Any, Dict, Literal

import dotenv
from gw.errors import GwTypeError
from gw.utils import is_pascal_case, pascal_to_snake, snake_to_pascal
from pydantic import BaseModel, Field, field_validator

from gwbase.config import EnumSettings
from gwbase.enums import SupervisorContainerStatus

ENCODE_ENUMS = EnumSettings(_env_file=dotenv.find_dotenv()).encode

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class SupervisorContainerGt(BaseModel):
    """
    Used to send and receive updates about SupervisorContainers.

    Sent from a GNodeRegistry to a World, and used also by the World as it spawns GNodeInstances
    in docker instances (i.e., the SupervisorContainers).

    [More info](https://gridworks.readthedocs.io/en/latest/supervisor.html)
    """

    supervisor_container_id: str = Field(
        title="Id of the docker SupervisorContainer",
    )
    status: SupervisorContainerStatus = Field(
        title="Status",
    )
    world_instance_name: str = Field(
        title="Name of the WorldInstance",
        description=(
            "For example, d1__1 is a potential name for a World whose World GNode has alias d1."
        ),
    )
    supervisor_g_node_instance_id: str = Field(
        title="Id of the SupervisorContainer's prime actor (aka the Supervisor GNode)",
    )
    supervisor_g_node_alias: str = Field(
        title="Alias of the SupervisorContainer's prime actor (aka the Supervisor GNode)",
    )
    type_name: Literal["supervisor.container.gt"] = "supervisor.container.gt"
    version: Literal["000"] = "000"

    class Config:
        extra = "allow"
        populate_by_name = True
        alias_generator = snake_to_pascal

    @field_validator("supervisor_container_id")
    @classmethod
    def _check_supervisor_container_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"SupervisorContainerId failed UuidCanonicalTextual format validation: {e}",
            ) from e
        return v

    @field_validator("world_instance_name")
    @classmethod
    def _check_world_instance_name(cls, v: str) -> str:
        try:
            check_is_world_instance_name_format(v)
        except ValueError as e:
            raise ValueError(
                f"WorldInstanceName failed WorldInstanceNameFormat format validation: {e}",
            ) from e
        return v

    @field_validator("supervisor_g_node_instance_id")
    @classmethod
    def _check_supervisor_g_node_instance_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"SupervisorGNodeInstanceId failed UuidCanonicalTextual format validation: {e}",
            ) from e
        return v

    @field_validator("supervisor_g_node_alias")
    @classmethod
    def _check_supervisor_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"SupervisorGNodeAlias failed LeftRightDot format validation: {e}",
            ) from e
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Main step in serializing the object. Encodes enums as their 8-digit random hex symbol if
        settings.encode_enums = 1.
        """
        if ENCODE_ENUMS:
            return self.enum_encoded_dict()
        else:
            return self.plain_enum_dict()

    def plain_enum_dict(self) -> Dict[str, Any]:
        """
        Returns enums as their values.
        """
        d = {
            snake_to_pascal(key): value
            for key, value in self.model_dump().items()
            if value is not None
        }
        d["Status"] = d["Status"].value
        return d

    def enum_encoded_dict(self) -> Dict[str, Any]:
        """
        Encodes enums as their 8-digit random hex symbol
        """
        d = {
            snake_to_pascal(key): value
            for key, value in self.model_dump().items()
            if value is not None
        }
        del d["Status"]
        d["StatusGtEnumSymbol"] = SupervisorContainerStatus.value_to_symbol(self.status)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the supervisor.container.gt.000 representation designed to send in a message.

        Recursively encodes enums as hard-to-remember 8-digit random hex symbols
        unless settings.encode_enums is set to 0.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SupervisorContainerGt_Maker:
    type_name = "supervisor.container.gt"
    version = "000"

    @classmethod
    def tuple_to_type(cls, tuple: SupervisorContainerGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, b: bytes) -> SupervisorContainerGt:
        """
        Given the bytes in a message, returns the corresponding class object.

        Args:
            b (bytes): candidate type instance

        Raises:
           GwTypeError: if the bytes are not a supervisor.container.gt.000 type

        Returns:
            SupervisorContainerGt instance
        """
        try:
            d = json.loads(b)
        except TypeError as e:
            raise GwTypeError("Type must be string or bytes!") from e
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing  must result in dict!\n <{b}>")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> SupervisorContainerGt:
        """
        Translates a dict representation of a supervisor.container.gt.000 message object
        into the Python class object.
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
        d2 = dict(d)
        if "SupervisorContainerId" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorContainerId: <{d2}>")
        if "StatusGtEnumSymbol" in d2.keys():
            value = SupervisorContainerStatus.symbol_to_value(d2["StatusGtEnumSymbol"])
            d2["Status"] = SupervisorContainerStatus(value)
            del d2["StatusGtEnumSymbol"]
        elif "Status" in d2.keys():
            if d2["Status"] not in SupervisorContainerStatus.values():
                d2["Status"] = SupervisorContainerStatus.default()
            else:
                d2["Status"] = SupervisorContainerStatus(d2["Status"])
        else:
            raise GwTypeError(
                f"both StatusGtEnumSymbol and Status missing from dict <{d2}>",
            )
        if "WorldInstanceName" not in d2.keys():
            raise GwTypeError(f"dict missing WorldInstanceName: <{d2}>")
        if "SupervisorGNodeInstanceId" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorGNodeInstanceId: <{d2}>")
        if "SupervisorGNodeAlias" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorGNodeAlias: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret supervisor.container.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        d3 = {pascal_to_snake(key): value for key, value in d2.items()}
        return SupervisorContainerGt(**d3)


def check_is_left_right_dot(v: str) -> None:
    """Checks LeftRightDot Format

    LeftRightDot format: Lowercase alphanumeric words separated by periods, with
    the most significant word (on the left) starting with an alphabet character.

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not LeftRightDot format
    """
    from typing import List

    try:
        x: List[str] = v.split(".")
    except Exception as e:
        raise ValueError(f"Failed to seperate <{v}> into words with split'.'") from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word of <{v}> must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of <{v}> split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of <{v}> must be lowercase.")


def check_is_uuid_canonical_textual(v: str) -> None:
    """Checks UuidCanonicalTextual format

    UuidCanonicalTextual format:  A string of hex words separated by hyphens
    of length 8-4-4-4-12.

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not UuidCanonicalTextual format
    """
    try:
        x = v.split("-")
    except AttributeError as e:
        raise ValueError(f"Failed to split on -: {e}") from e
    if len(x) != 5:
        raise ValueError(f"<{v}> split by '-' did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError as e:
            raise ValueError(f"Words of <{v}> are not all hex") from e
    if len(x[0]) != 8:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[1]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[2]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[3]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[4]) != 12:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")


def check_is_world_instance_name_format(v: str) -> None:
    """Checks WorldInstanceName Format

    WorldInstanceName format: A single alphanumerical word starting
    with an alphabet char (the root GNodeAlias) and an integer,
    seperated by '__'. For example 'd1__1'

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not WorldInstanceNameFormat format
    """
    try:
        words = v.split("__")
    except Exception as e:
        raise ValueError(f"<{v}> is not split by '__'") from e
    if len(words) != 2:
        raise ValueError(f"<{v}> not 2 words separated by '__'")
    try:
        int(words[1])
    except Exception as e:
        raise ValueError(f"<{v}> second word not an int") from e

    root_g_node_alias = words[0]
    first_char = root_g_node_alias[0]
    if not first_char.isalpha():
        raise ValueError(f"<{v}> first word must be alph char")
    if not root_g_node_alias.isalnum():
        raise ValueError(f"<{v}> first word must be alphanumeric")
