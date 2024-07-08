"""Type super.starter, version 000"""

import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from gw.errors import GwTypeError
from gw.utils import is_pascal_case
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic.alias_generators import to_pascal
from pydantic.alias_generators import to_snake

from gwbase.types.g_node_instance_gt import GNodeInstanceGt
from gwbase.types.g_node_instance_gt import GNodeInstanceGt_Maker
from gwbase.types.supervisor_container_gt import SupervisorContainerGt
from gwbase.types.supervisor_container_gt import SupervisorContainerGt_Maker


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
        alias_generator = to_pascal

    @field_validator("alias_with_key_list")
    def _check_alias_with_key_list(cls, v: List[str]) -> List[str]:
        for elt in v:
            try:
                check_is_left_right_dot(elt)
            except ValueError as e:
                raise ValueError(
                    f"AliasWithKeyList element {elt} failed LeftRightDot format validation: {e}"
                )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        super.starter.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        super.starter.000 type. Unlike the standard python dict method,
        it makes the following substantive changes:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.
        """
        d = {
            to_pascal(key): value
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
        Serialize to the super.starter.000 representation.

        Instances in the class are python-native representations of super.starter.000
        objects, while the actual super.starter.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is SuperStarter.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
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
    def type_to_tuple(cls, t: bytes) -> SuperStarter:
        """
        Given a serialized JSON type object, returns the Python class object.
        """
        try:
            d = json.loads(t)
        except TypeError:
            raise GwTypeError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing <{t}> must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> SuperStarter:
        """
        Deserialize a dictionary representation of a super.starter.000 message object
        into a SuperStarter python object for internal use.

        This is the near-inverse of the SuperStarter.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a GwTypeError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           GwTypeError: if the dict cannot be turned into a SuperStarter object.

        Returns:
            SuperStarter
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
        d2 = dict(d)
        if "SupervisorContainer" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorContainer: <{d2}>")
        if not isinstance(d2["SupervisorContainer"], dict):
            raise GwTypeError(
                f"SupervisorContainer <{d2['SupervisorContainer']}> must be a SupervisorContainerGt!"
            )
        supervisor_container = SupervisorContainerGt_Maker.dict_to_tuple(
            d2["SupervisorContainer"]
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
                    f"GniList <{d2['GniList']}> must be a List of GNodeInstanceGt types"
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
                f"Attempting to interpret super.starter version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        d3 = {to_snake(key): value for key, value in d2.items()}
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
            f"Most significant word of <{v}> must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of <{v}> split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of <{v}> must be lowercase.")
