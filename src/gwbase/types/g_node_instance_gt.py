"""Type g.node.instance.gt, version 000"""

import json
import logging
from typing import Any, Dict, Literal, Optional

import dotenv
from gw.errors import DcError, GwTypeError
from gw.utils import is_pascal_case, pascal_to_snake, snake_to_pascal
from pydantic import BaseModel, Field, field_validator

from gwbase.config import EnumSettings
from gwbase.data_classes.g_node import GNode
from gwbase.data_classes.g_node_instance import GNodeInstance
from gwbase.enums import GniStatus, StrategyName

ENCODE_ENUMS = EnumSettings(_env_file=dotenv.find_dotenv()).encode

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class GNodeInstanceGt(BaseModel):
    """
    Used to send and receive updates about GNodeInstances.

    One of the layers of abstraction connecting a GNode with a running app in a Docker container.

    [More info](https://gridworks.readthedocs.io/en/latest/g-node-instance.html)
    """

    g_node_instance_id: str = Field(
        title="Immutable identifier for GNodeInstance (Gni)",
    )
    g_node_id: str = Field(
        title="The GNode represented by the Gni",
    )
    strategy: StrategyName = Field(
        title="Used to determine the code running in a GNode actor application",
    )
    status: GniStatus = Field(
        title="Lifecycle Status for Gni",
    )
    supervisor_container_id: str = Field(
        title="The Id of the docker container where the Gni runs",
    )
    start_time_unix_s: int = Field(
        title="When the gni starts representing the GNode",
        description=(
            "Specifically, when the Status changes from Pending to Active. Note that this is "
            "time in the GNode's World, which may not be real time if it is a simulation."
        ),
    )
    end_time_unix_s: int = Field(
        title="When the gni stops representing the GNode",
        description="Specifically, when the Status changes from Active to Done.",
    )
    algo_address: Optional[str] = Field(
        title="Algorand address for Gni",
        default=None,
    )
    type_name: Literal["g.node.instance.gt"] = "g.node.instance.gt"
    version: Literal["000"] = "000"

    class Config:
        extra = "allow"
        populate_by_name = True
        alias_generator = snake_to_pascal

    @field_validator("g_node_instance_id")
    def _check_g_node_instance_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeInstanceId failed UuidCanonicalTextual format validation: {e}",
            )
        return v

    @field_validator("g_node_id")
    def _check_g_node_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeId failed UuidCanonicalTextual format validation: {e}",
            )
        return v

    @field_validator("supervisor_container_id")
    def _check_supervisor_container_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"SupervisorContainerId failed UuidCanonicalTextual format validation: {e}",
            )
        return v

    @field_validator("start_time_unix_s")
    def _check_start_time_unix_s(cls, v: int) -> int:
        try:
            check_is_reasonable_unix_time_s(v)
        except ValueError as e:
            raise ValueError(
                f"StartTimeUnixS failed ReasonableUnixTimeS format validation: {e}",
            )
        return v

    @field_validator("algo_address")
    def _check_algo_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"AlgoAddress failed AlgoAddressStringFormat format validation: {e}",
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
        d["Strategy"] = d["Strategy"].value
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
        del d["Strategy"]
        d["StrategyGtEnumSymbol"] = StrategyName.value_to_symbol(self.strategy)
        del d["Status"]
        d["StatusGtEnumSymbol"] = GniStatus.value_to_symbol(self.status)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the g.node.instance.gt.000 representation designed to send in a message.

        Recursively encodes enums as hard-to-remember 8-digit random hex symbols
        unless settings.encode_enums is set to 0.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class GNodeInstanceGt_Maker:
    type_name = "g.node.instance.gt"
    version = "000"

    @classmethod
    def tuple_to_type(cls, tuple: GNodeInstanceGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, b: bytes) -> GNodeInstanceGt:
        """
        Given the bytes in a message, returns the corresponding class object.

        Args:
            b (bytes): candidate type instance

        Raises:
           GwTypeError: if the bytes are not a g.node.instance.gt.000 type

        Returns:
            GNodeInstanceGt instance
        """
        try:
            d = json.loads(b)
        except TypeError:
            raise GwTypeError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing  must result in dict!\n <{b}>")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> GNodeInstanceGt:
        """
        Translates a dict representation of a g.node.instance.gt.000 message object
        into the Python class object.
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
        d2 = dict(d)
        if "GNodeInstanceId" not in d2.keys():
            raise GwTypeError(f"dict missing GNodeInstanceId: <{d2}>")
        if "GNodeId" not in d2.keys():
            raise GwTypeError(f"dict missing GNode: <{d2}>")
        if "StrategyGtEnumSymbol" in d2.keys():
            value = StrategyName.symbol_to_value(d2["StrategyGtEnumSymbol"])
            d2["Strategy"] = StrategyName(value)
            del d2["StrategyGtEnumSymbol"]
        elif "Strategy" in d2.keys():
            if d2["Strategy"] not in StrategyName.values():
                d2["Strategy"] = StrategyName.default()
            else:
                d2["Strategy"] = StrategyName(d2["Strategy"])
        else:
            raise GwTypeError(
                f"both StrategyGtEnumSymbol and Strategy missing from dict <{d2}>",
            )
        if "StatusGtEnumSymbol" in d2.keys():
            value = GniStatus.symbol_to_value(d2["StatusGtEnumSymbol"])
            d2["Status"] = GniStatus(value)
            del d2["StatusGtEnumSymbol"]
        elif "Status" in d2.keys():
            if d2["Status"] not in GniStatus.values():
                d2["Status"] = GniStatus.default()
            else:
                d2["Status"] = GniStatus(d2["Status"])
        else:
            raise GwTypeError(
                f"both StatusGtEnumSymbol and Status missing from dict <{d2}>",
            )
        if "SupervisorContainerId" not in d2.keys():
            raise GwTypeError(f"dict missing SupervisorContainerId: <{d2}>")
        if "StartTimeUnixS" not in d2.keys():
            raise GwTypeError(f"dict missing StartTimeUnixS: <{d2}>")
        if "EndTimeUnixS" not in d2.keys():
            raise GwTypeError(f"dict missing EndTimeUnixS: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret g.node.instance.gt version {d2['Version']} as version 000",
            )
            d2["Version"] = "000"
        d3 = {pascal_to_snake(key): value for key, value in d2.items()}
        return GNodeInstanceGt(**d3)

    @classmethod
    def tuple_to_dc(cls, t: GNodeInstanceGt) -> GNodeInstance:
        if t.g_node_instance_id in GNodeInstance.by_id.keys():
            dc = GNodeInstance.by_id[t.g_node_instance_id]
        else:
            try:
                g_node = GNode.by_id[t.g_node_id]
            except:
                raise DcError(f"Missing GNode with id {t.g_node_id}")
            dc = GNodeInstance(
                g_node_instance_id=t.g_node_instance_id,
                g_node=g_node,
                strategy=t.strategy,
                status=t.status,
                supervisor_container_id=t.supervisor_container_id,
                start_time_unix_s=t.start_time_unix_s,
                end_time_unix_s=t.end_time_unix_s,
                algo_address=t.algo_address,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: GNodeInstance) -> GNodeInstanceGt:
        return GNodeInstanceGt(
            g_node_instance_id=dc.g_node_instance_id,
            g_node_id=dc.g_node_id,
            strategy=dc.strategy,
            status=dc.status,
            supervisor_container_id=dc.supervisor_container_id,
            start_time_unix_s=dc.start_time_unix_s,
            end_time_unix_s=dc.end_time_unix_s,
            algo_address=dc.algo_address,
        )

    @classmethod
    def type_to_dc(cls, t: str) -> GNodeInstance:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: GNodeInstance) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> GNodeInstance:
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
        at.decode(at.encode(v))
    except Exception as e:
        raise ValueError(f"Not AlgoAddressStringFormat: {e}")


def check_is_reasonable_unix_time_s(v: int) -> None:
    """Checks ReasonableUnixTimeS format

    ReasonableUnixTimeS format: unix seconds between Jan 1 2000 and Jan 1 3000

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v is not ReasonableUnixTimeS format
    """
    from datetime import datetime, timezone

    start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(3000, 1, 1, tzinfo=timezone.utc)

    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    if v < start_timestamp:
        raise ValueError(f"{v} must be after Jan 1 2000")
    if v > end_timestamp:
        raise ValueError(f"{v} must be before Jan 1 3000")


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
