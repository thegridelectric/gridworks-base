"""Type super.starter, version 000"""

import json
import logging
from typing import Any, Dict, List, Literal

import dotenv
from gw.errors import GwTypeError
from gw.utils import is_pascal_case, pascal_to_snake, snake_to_pascal
from pydantic import BaseModel, Field, field_validator

from gwbase.config import EnumSettings
from gwbase.types.g_node_instance_gt import GNodeInstanceGt, GNodeInstanceGt_Maker
from gwbase.types.supervisor_container_gt import (
    SupervisorContainerGt,
    SupervisorContainerGt_Maker,
)

ENCODE_ENUMS = EnumSettings(_env_file=dotenv.find_dotenv()).encode

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class SuperStarter(BaseModel):
    """
    Used by world to seed a docker container with data needed to spawn and superviser GNodeInstances
    """

    supervisor_container: SupervisorContainerGt = Field(
        title="Key data about the docker container",
    )
    gni_list: List[GNodeInstanceGt] = Field(
        title="List of GNodeInstances (Gnis) run in the container",
    )
    alias_with_key_list: List[str] = Field(
        title="Aliases of Gnis that own Algorand secret keys",
    )
    key_list: List[str] = Field(
        title="Algorand secret keys owned by Gnis",
    )
    type_name: Literal["super.starter"] = "super.starter"
    version: Literal["000"] = "000"

    class Config:
        extra = "allow"
        populate_by_name = True
        alias_generator = snake_to_pascal

    @field_validator("alias_with_key_list")
    def _check_alias_with_key_list(cls, v: List[str]) -> List[str]:
        for elt in v:
            try:
                check_is_left_right_dot(elt)
            except ValueError as e:
                raise ValueError(
                    f"AliasWithKeyList element {elt} failed LeftRightDot format validation: {e}",
                )
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
        d["SupervisorContainer"] = self.supervisor_container.as_dict()
        # Recursively calling as_dict()
        gni_list = []
        for elt in self.gni_list:
            gni_list.append(elt.as_dict())
        d["GniList"] = gni_list
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
        d["SupervisorContainer"] = self.supervisor_container.as_dict()
        # Recursively calling as_dict()
        gni_list = []
        for elt in self.gni_list:
            gni_list.append(elt.as_dict())
        d["GniList"] = gni_list
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the super.starter.000 representation designed to send in a message.

        Recursively encodes enums as hard-to-remember 8-digit random hex symbols
        unless settings.encode_enums is set to 0.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SuperStarter_Maker:
    type_name = "super.starter"
    version = "000"

    @classmethod
    def tuple_to_type(cls, tuple: SuperStarter) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, b: bytes) -> SuperStarter:
        """
        Given the bytes in a message, returns the corresponding class object.

        Args:
            b (bytes): candidate type instance

        Raises:
           GwTypeError: if the bytes are not a super.starter.000 type

        Returns:
            SuperStarter instance
        """
        try:
            d = json.loads(b)
        except TypeError:
            raise GwTypeError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing  must result in dict!\n <{b}>")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> SuperStarter:
        """
        Translates a dict representation of a super.starter.000 message object
        into the Python class object.
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
        d2 = dict(d)
        if "SupervisorContainer" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorContainer: <{d2}>")
        if not isinstance(d2["SupervisorContainer"], dict):
            raise GwTypeError(
                f"SupervisorContainer <{d2['SupervisorContainer']}> must be a SupervisorContainerGt!",
            )
        supervisor_container = SupervisorContainerGt_Maker.dict_to_tuple(
            d2["SupervisorContainer"],
        )
        d2["SupervisorContainer"] = supervisor_container
        if "GniList" not in d2.keys():
            raise GwTypeError(f"dict missing GniList: <{d2}>")
        if not isinstance(d2["GniList"], List):
            raise GwTypeError(f"GniList <{d2['GniList']}> must be a List!")
        gni_list = []
        for elt in d2["GniList"]:
            if not isinstance(elt, dict):
                raise GwTypeError(
                    f"GniList <{d2['GniList']}> must be a List of GNodeInstanceGt types",
                )
            t = GNodeInstanceGt_Maker.dict_to_tuple(elt)
            gni_list.append(t)
        d2["GniList"] = gni_list
        if "AliasWithKeyList" not in d2.keys():
            raise GwTypeError(f"dict missing AliasWithKeyList: <{d2}>")
        if "KeyList" not in d2.keys():
            raise GwTypeError(f"dict missing KeyList: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret super.starter version {d2['Version']} as version 000",
            )
            d2["Version"] = "000"
        d3 = {pascal_to_snake(key): value for key, value in d2.items()}
        return SuperStarter(**d3)


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
    except:
        raise ValueError(f"Failed to seperate <{v}> into words with split'.'")
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word of <{v}> must start with alphabet char.",
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of <{v}> split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of <{v}> must be lowercase.")
