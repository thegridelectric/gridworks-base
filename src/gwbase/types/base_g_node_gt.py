"""Type base.g.node.gt, version 002"""

import json
import logging
from typing import Any, Dict, Literal, Optional

import algosdk
import dotenv
from gw.errors import GwTypeError
from gw.utils import is_pascal_case, pascal_to_snake, snake_to_pascal
from pydantic import BaseModel, Field, field_validator

from gwbase.config import EnumSettings
from gwbase.data_classes.base_g_node import BaseGNode
from gwbase.enums import CoreGNodeRole, GNodeStatus

ENCODE_ENUMS = EnumSettings(_env_file=dotenv.find_dotenv()).encode

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class BaseGNodeGt(BaseModel):
    """
    BaseGNode. Authority is GNodeFactory. New attributes: PrevAlias, OwnerAddr, DaemonAddr,
    TradingRightsNftId. CHANGE to TOPOLOGY Axiom (Joint Axiom 1)
    """

    g_node_id: str = Field(
        title="GNodeId",
    )
    alias: str = Field(
        title="Alias",
    )
    status: GNodeStatus = Field(
        title="Status",
    )
    role: CoreGNodeRole = Field(
        title="Role",
    )
    g_node_registry_addr: str = Field(
        title="GNodeRegistryAddr",
    )
    prev_alias: Optional[str] = Field(
        title="PrevAlias",
        default=None,
    )
    gps_point_id: Optional[str] = Field(
        title="GpsPointId",
        default=None,
    )
    ownership_deed_id: Optional[int] = Field(
        title="OwnershipDeedId",
        default=None,
    )
    ownership_deed_validator_addr: Optional[str] = Field(
        title="OwnershipDeedValidatorAddr",
        default=None,
    )
    owner_addr: Optional[str] = Field(
        title="OwnerAddr",
        default=None,
    )
    daemon_addr: Optional[str] = Field(
        title="DaemonAddr",
        default=None,
    )
    trading_rights_id: Optional[int] = Field(
        title="TradingRightsId",
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
    type_name: Literal["base.g.node.gt"] = "base.g.node.gt"
    version: Literal["002"] = "002"

    class Config:
        extra = "allow"
        populate_by_name = True
        alias_generator = snake_to_pascal

    @field_validator("g_node_id")
    @classmethod
    def _check_g_node_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeId failed UuidCanonicalTextual format validation: {e}",
            ) from e
        return v

    @field_validator("alias")
    @classmethod
    def _check_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"Alias failed LeftRightDot format validation: {e}") from e
        return v

    @field_validator("g_node_registry_addr")
    @classmethod
    def _check_g_node_registry_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeRegistryAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("prev_alias")
    @classmethod
    def _check_prev_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"PrevAlias failed LeftRightDot format validation: {e}"
            ) from e
        return v

    @field_validator("gps_point_id")
    @classmethod
    def _check_gps_point_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GpsPointId failed UuidCanonicalTextual format validation: {e}",
            ) from e
        return v

    @field_validator("ownership_deed_id")
    @classmethod
    def _check_ownership_deed_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"OwnershipDeedId failed PositiveInteger format validation: {e}",
            ) from e
        return v

    @field_validator("ownership_deed_validator_addr")
    @classmethod
    def _check_ownership_deed_validator_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnershipDeedValidatorAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("owner_addr")
    @classmethod
    def _check_owner_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnerAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("daemon_addr")
    @classmethod
    def _check_daemon_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"DaemonAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("trading_rights_id")
    @classmethod
    def _check_trading_rights_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"TradingRightsId failed PositiveInteger format validation: {e}",
            ) from e
        return v

    @field_validator("scada_algo_addr")
    @classmethod
    def _check_scada_algo_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaAlgoAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("scada_cert_id")
    @classmethod
    def _check_scada_cert_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaCertId failed PositiveInteger format validation: {e}",
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
        d["Role"] = d["Role"].value
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
        d["StatusGtEnumSymbol"] = GNodeStatus.value_to_symbol(self.status)
        del d["Role"]
        d["RoleGtEnumSymbol"] = CoreGNodeRole.value_to_symbol(self.role)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the base.g.node.gt.002 representation designed to send in a message.

        Recursively encodes enums as hard-to-remember 8-digit random hex symbols
        unless settings.encode_enums is set to 0.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class BaseGNodeGt_Maker:
    type_name = "base.g.node.gt"
    version = "002"

    @classmethod
    def tuple_to_type(cls, tuple: BaseGNodeGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, b: bytes) -> BaseGNodeGt:
        """
        Given the bytes in a message, returns the corresponding class object.

        Args:
            b (bytes): candidate type instance

        Raises:
           GwTypeError: if the bytes are not a base.g.node.gt.002 type

        Returns:
            BaseGNodeGt instance
        """
        try:
            d = json.loads(b)
        except TypeError as e:
            raise GwTypeError("Type must be string or bytes!") from e
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing  must result in dict!\n <{b}>")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> BaseGNodeGt:
        """
        Translates a dict representation of a base.g.node.gt.002 message object
        into the Python class object.
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
        d2 = dict(d)
        if "GNodeId" not in d2.keys():
            raise GwTypeError(f"dict missing GNodeId: <{d2}>")
        if "Alias" not in d2.keys():
            raise GwTypeError(f"dict missing Alias: <{d2}>")
        if "StatusGtEnumSymbol" in d2.keys():
            value = GNodeStatus.symbol_to_value(d2["StatusGtEnumSymbol"])
            d2["Status"] = GNodeStatus(value)
            del d2["StatusGtEnumSymbol"]
        elif "Status" in d2.keys():
            if d2["Status"] not in GNodeStatus.values():
                d2["Status"] = GNodeStatus.default()
            else:
                d2["Status"] = GNodeStatus(d2["Status"])
        else:
            raise GwTypeError(
                f"both StatusGtEnumSymbol and Status missing from dict <{d2}>",
            )
        if "RoleGtEnumSymbol" in d2.keys():
            value = CoreGNodeRole.symbol_to_value(d2["RoleGtEnumSymbol"])
            d2["Role"] = CoreGNodeRole(value)
            del d2["RoleGtEnumSymbol"]
        elif "Role" in d2.keys():
            if d2["Role"] not in CoreGNodeRole.values():
                d2["Role"] = CoreGNodeRole.default()
            else:
                d2["Role"] = CoreGNodeRole(d2["Role"])
        else:
            raise GwTypeError(
                f"both RoleGtEnumSymbol and Role missing from dict <{d2}>",
            )
        if "GNodeRegistryAddr" not in d2.keys():
            raise GwTypeError(f"dict missing GNodeRegistryAddr: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "002":
            LOGGER.debug(
                f"Attempting to interpret base.g.node.gt version {d2['Version']} as version 002"
            )
            d2["Version"] = "002"
        d3 = {pascal_to_snake(key): value for key, value in d2.items()}
        return BaseGNodeGt(**d3)

    @classmethod
    def tuple_to_dc(cls, t: BaseGNodeGt) -> BaseGNode:
        if t.g_node_id in BaseGNode.by_id.keys():
            dc = BaseGNode.by_id[t.g_node_id]
        else:
            dc = BaseGNode(
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
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: BaseGNode) -> BaseGNodeGt:
        return BaseGNodeGt(
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
        )

    @classmethod
    def type_to_dc(cls, t: str) -> BaseGNode:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: BaseGNode) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> BaseGNode:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))


def check_is_algo_address_string_format(v: str) -> None:
    """
    AlgoAddressStringFormat format: The public key of a private/public Ed25519
    key pair, transformed into an  Algorand address, by adding a 4-byte checksum
    to the end of the public key and then encoding in base32.

    Raises:
        ValueError: if not AlgoAddressStringFormat format
    """

    at = algosdk.abi.AddressType()
    try:
        at.decode(at.encode(v))
    except Exception as e:
        raise ValueError(f"Not AlgoAddressStringFormat: {e}") from e


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
