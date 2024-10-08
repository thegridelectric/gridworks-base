GNodeGt
==========================
Python pydantic class corresponding to json type `g.node.gt`, version `002`.

.. autoclass:: gwbase.types.GNodeGt
    :members:

**GNodeId**:
    - Description: Immutable identifier for GNode.
    - Format: UuidCanonicalTextual

**Alias**:
    - Description: Structured mutable identifier for GNode.The GNode Aliases are used for organizing how actors in Gridworks communicate. Together, they also encode the known topology of the electric grid.
    - Format: LeftRightDot

**Status**:
    - Description: Lifecycle indicator.

**Role**:
    - Description: Role within Gridworks.

**GNodeRegistryAddr**:
    - Description: Algorand address for GNodeRegistry.For actors in a Gridworks world, the GNodeRegistry is the Single Source of Truth for existence and updates to GNodes.
    - Format: AlgoAddressStringFormat

**PrevAlias**:
    - Description: Previous GNodeAlias.As the topology of the grid updates, GNodeAliases will change to reflect that. This may happen a handful of times over the life of a GNode.
    - Format: LeftRightDot

**GpsPointId**:
    - Description: Lat/lon of GNode.Some GNodes, in particular those acting as avatars for physical devices that are part of or are attached to the electric grid, have physical locations. These locations are used to help validate the grid topology.
    - Format: UuidCanonicalTextual

**OwnershipDeedId**:
    - Description: Algorand Id of ASA Deed.The Id of the TaDeed Algorand Standard Asset if the GNode is a TerminalAsset.
    - Format: PositiveInteger

**OwnershipDeedValidatorAddr**:
    - Description: Algorand address of Validator.Deeds are issued by the GNodeFactory, in partnership with third party Validators.
    - Format: AlgoAddressStringFormat

**OwnerAddr**:
    - Description: Algorand address of the deed owner.
    - Format: AlgoAddressStringFormat

**DaemonAddr**:
    - Description: Algorand address of the daemon app.Some GNodes have Daemon applications associated to them to handle blockchain operations.
    - Format: AlgoAddressStringFormat

**TradingRightsId**:
    - Description: Algorand Id of ASA TradingRights.The Id of the TradingRights Algorand Standard Asset.
    - Format: PositiveInteger

**ScadaAlgoAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**ScadaCertId**:
    - Description:
    - Format: PositiveInteger

**ComponentId**:
    - Description: Unique identifier for GNode's Component.Used if a GNode is an avatar for a physical device. The serial number of a device is different from its make/model. The ComponentId captures the specific instance of the device.
    - Format: UuidCanonicalTextual

**DisplayName**:
    - Description: Display Name.Sample: Keene Oak's Atomic TNode

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.g_node_gt.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.g_node_gt.check_is_positive_integer
    :members:


.. autoclass:: gwbase.types.g_node_gt.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.g_node_gt.check_is_algo_address_string_format
    :members:


.. autoclass:: gwbase.types.GNodeGt_Maker
    :members:
