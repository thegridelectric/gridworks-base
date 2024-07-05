"""Type g.node.gt, version 002"""

import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from gw.errors import GwTypeError
from gw.utils import snake_to_camel
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import validator

from gwbase.data_classes.g_node import GNode
from gwbase.enums import GNodeRole
from gwbase.enums import GNodeStatus


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class GNodeGt(BaseModel):
    """
    Used to send and receive updates about GNodes.

    GNodes are the building blocks of Gridworks. They have slowly-changing state that must be
    kept in sync across a distributed system. Therefore, they require a global registry to act
    as Single Source of Truth (SSoT). This class is used for that SSoT to share information
    with actors about their GNodes, and the GNodes that they will observe and communicate with.

    [More info](https://gridworks.readthedocs.io/en/latest/g-node.html)
    """

    g_node_id: str = Field(
        title="Immutable identifier for GNode",
    )
    alias: str = Field(
        title="Structured mutable identifier for GNode",
        description=(
            "The GNode Aliases are used for organizing how actors in Gridworks communicate. Together, "
            "they also encode the known topology of the electric grid."
            "[More info](https://gridworks.readthedocs.io/en/latest/g-node-alias.html)"
        ),
    )
    status: GNodeStatus = Field(
        title="Lifecycle indicator",
    )
    role: GNodeRole = Field(
        title="Role within Gridworks",
        description="[More info](https://gridworks.readthedocs.io/en/latest/g-node-role.html)",
    )
    g_node_registry_addr: str = Field(
        title="Algorand address for GNodeRegistry",
        description=(
            "For actors in a Gridworks world, the GNodeRegistry is the Single Source of Truth "
            "for existence and updates to GNodes."
            "[More info](https://gridworks.readthedocs.io/en/latest/g-node-registry.html)"
        ),
    )
    prev_alias: Optional[str] = Field(
        title="Previous GNodeAlias",
        description=(
            "As the topology of the grid updates, GNodeAliases will change to reflect that. This "
            "may happen a handful of times over the life of a GNode."
        ),
        default=None,
    )
    gps_point_id: Optional[str] = Field(
        title="Lat/lon of GNode",
        description=(
            "Some GNodes, in particular those acting as avatars for physical devices that are "
            "part of or are attached to the electric grid, have physical locations. These locations "
            "are used to help validate the grid topology."
        ),
        default=None,
    )
    ownership_deed_id: Optional[int] = Field(
        title="Algorand Id of ASA Deed",
        description=(
            "The Id of the TaDeed Algorand Standard Asset if the GNode is a TerminalAsset."
            "[More info](https://gridworks.readthedocs.io/en/latest/ta-deed.html)"
        ),
        default=None,
    )
    ownership_deed_validator_addr: Optional[str] = Field(
        title="Algorand address of Validator",
        description=(
            "Deeds are issued by the GNodeFactory, in partnership with third party Validators."
            "[More info](https://gridworks.readthedocs.io/en/latest/ta-validator.html)"
        ),
        default=None,
    )
    owner_addr: Optional[str] = Field(
        title="Algorand address of the deed owner",
        default=None,
    )
    daemon_addr: Optional[str] = Field(
        title="Algorand address of the daemon app",
        description=(
            "Some GNodes have Daemon applications associated to them to handle blockchain operations."
        ),
        default=None,
    )
    trading_rights_id: Optional[int] = Field(
        title="Algorand Id of ASA TradingRights",
        description="The Id of the TradingRights Algorand Standard Asset.",
        default=None,
    )
    scada_algo_addr: Optional[str] = Field(
        title="ScadaAlgoAddr",
        default=None,
    )
    scada_cert_id: Optional[int] = Field(
        title="ScadaCertId",
        default=None,
    )
    component_id: Optional[str] = Field(
        title="Unique identifier for GNode's Component",
        description=(
            "Used if a GNode is an avatar for a physical device. The serial number of a device "
            "is different from its make/model. The ComponentId captures the specific instance "
            "of the device."
        ),
        default=None,
    )
    display_name: Optional[str] = Field(
        title="Display Name",
        description="Sample: Keene Oak's Atomic TNode",
        default=None,
    )
    type_name: Literal["g.node.gt"] = "g.node.gt"
    version: Literal["002"] = "002"

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True
        alias_generator = snake_to_camel

    @validator("g_node_id")
    def _check_g_node_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("alias")
    def _check_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"Alias failed LeftRightDot format validation: {e}")
        return v

    @validator("g_node_registry_addr")
    def _check_g_node_registry_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeRegistryAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("prev_alias")
    def _check_prev_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"PrevAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("gps_point_id")
    def _check_gps_point_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GpsPointId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("ownership_deed_id")
    def _check_ownership_deed_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"OwnershipDeedId failed PositiveInteger format validation: {e}"
            )
        return v

    @validator("ownership_deed_validator_addr")
    def _check_ownership_deed_validator_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnershipDeedValidatorAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("owner_addr")
    def _check_owner_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnerAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("daemon_addr")
    def _check_daemon_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"DaemonAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("trading_rights_id")
    def _check_trading_rights_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"TradingRightsId failed PositiveInteger format validation: {e}"
            )
        return v

    @validator("scada_algo_addr")
    def _check_scada_algo_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaAlgoAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("scada_cert_id")
    def _check_scada_cert_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaCertId failed PositiveInteger format validation: {e}"
            )
        return v

    @validator("component_id")
    def _check_component_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"ComponentId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        g.node.gt.002 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        g.node.gt.002 type. Unlike the standard python dict method,
        it makes the following substantive changes:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.
        """
        d = {
            key: value
            for key, value in self.dict(
                by_alias=True, include=self.__fields_set__ | {"type_name", "version"}
            ).items()
            if value is not None
        }
        del d["Status"]
        d["StatusGtEnumSymbol"] = GNodeStatus.value_to_symbol(self.status)
        del d["Role"]
        d["RoleGtEnumSymbol"] = GNodeRole.value_to_symbol(self.role)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the g.node.gt.002 representation.

        Instances in the class are python-native representations of g.node.gt.002
        objects, while the actual g.node.gt.002 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is GNodeGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class GNodeGt_Maker:
    type_name = "g.node.gt"
    version = "002"

    @classmethod
    def tuple_to_type(cls, tuple: GNodeGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> GNodeGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> GNodeGt:
        """
        Deserialize a dictionary representation of a g.node.gt.002 message object
        into a GNodeGt python object for internal use.

        This is the near-inverse of the GNodeGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a GwTypeError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           GwTypeError: if the dict cannot be turned into a GNodeGt object.

        Returns:
            GNodeGt
        """
        d2 = dict(d)
        if "GNodeId" not in d2.keys():
            raise GwTypeError(f"dict missing GNodeId: <{d2}>")
        if "Alias" not in d2.keys():
            raise GwTypeError(f"dict missing Alias: <{d2}>")
        if "StatusGtEnumSymbol" not in d2.keys():
            raise GwTypeError(f"StatusGtEnumSymbol missing from dict <{d2}>")
        value = GNodeStatus.symbol_to_value(d2["StatusGtEnumSymbol"])
        d2["Status"] = GNodeStatus(value)
        del d2["StatusGtEnumSymbol"]
        if "RoleGtEnumSymbol" not in d2.keys():
            raise GwTypeError(f"RoleGtEnumSymbol missing from dict <{d2}>")
        value = GNodeRole.symbol_to_value(d2["RoleGtEnumSymbol"])
        d2["Role"] = GNodeRole(value)
        del d2["RoleGtEnumSymbol"]
        if "GNodeRegistryAddr" not in d2.keys():
            raise GwTypeError(f"dict missing GNodeRegistryAddr: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "002":
            LOGGER.debug(
                f"Attempting to interpret g.node.gt version {d2['Version']} as version 002"
            )
            d2["Version"] = "002"
        return GNodeGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: GNodeGt) -> GNode:
        if t.g_node_id in GNode.by_id.keys():
            dc = GNode.by_id[t.g_node_id]
        else:
            dc = GNode(
                g_node_id=t.g_node_id,
                alias=t.alias,
                status=t.status,
                role=t.role,
                g_node_registry_addr=t.g_node_registry_addr,
                prev_alias=t.prev_alias,
                gps_point_id=t.gps_point_id,
                ownership_deed_id=t.ownership_deed_id,
                ownership_deed_validator_addr=t.ownership_deed_validator_addr,
                owner_addr=t.owner_addr,
                daemon_addr=t.daemon_addr,
                trading_rights_id=t.trading_rights_id,
                scada_algo_addr=t.scada_algo_addr,
                scada_cert_id=t.scada_cert_id,
                component_id=t.component_id,
                display_name=t.display_name,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: GNode) -> GNodeGt:
        return GNodeGt(
            g_node_id=dc.g_node_id,
            alias=dc.alias,
            status=dc.status,
            role=dc.role,
            g_node_registry_addr=dc.g_node_registry_addr,
            prev_alias=dc.prev_alias,
            gps_point_id=dc.gps_point_id,
            ownership_deed_id=dc.ownership_deed_id,
            ownership_deed_validator_addr=dc.ownership_deed_validator_addr,
            owner_addr=dc.owner_addr,
            daemon_addr=dc.daemon_addr,
            trading_rights_id=dc.trading_rights_id,
            scada_algo_addr=dc.scada_algo_addr,
            scada_cert_id=dc.scada_cert_id,
            component_id=dc.component_id,
            display_name=dc.display_name,
        )

    @classmethod
    def type_to_dc(cls, t: str) -> GNode:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: GNode) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> GNode:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))


def check_is_algo_address_string_format(v: str) -> None:
    """
    AlgoAddressStringFormat format: The public key of a private/public Ed25519
    key pair, transformed into an  Algorand address, by adding a 4-byte checksum
    to the end of the public key and then encoding in base32.

    Raises:
        ValueError: if not AlgoAddressStringFormat format
    """
    import algosdk

    at = algosdk.abi.AddressType()
    try:
        result = at.decode(at.encode(v))
    except Exception as e:
        raise ValueError(f"Not AlgoAddressStringFormat: {e}")


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


def check_is_positive_integer(v: int) -> None:
    """
    Must be positive when interpreted as an integer. Interpretation as an
    integer follows the pydantic rules for this - which will round down
    rational numbers. So 1.7 will be interpreted as 1 and is also fine,
    while 0.5 is interpreted as 0 and will raise an exception.

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v < 1
    """
    v2 = int(v)
    if v2 < 1:
        raise ValueError(f"<{v}> is not PositiveInteger")


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
        raise ValueError(f"Failed to split on -: {e}")
    if len(x) != 5:
        raise ValueError(f"<{v}> split by '-' did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            raise ValueError(f"Words of <{v}> are not all hex")
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
