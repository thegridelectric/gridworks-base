BaseGNodeGt
==========================
Python pydantic class corresponding to json type `base.g.node.gt`, version `002`.

.. autoclass:: gwbase.types.BaseGNodeGt
    :members:

**GNodeId**:
    - Description:
    - Format: UuidCanonicalTextual

**Alias**:
    - Description:
    - Format: LeftRightDot

**Status**:
    - Description:

**Role**:
    - Description:

**GNodeRegistryAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**PrevAlias**:
    - Description:
    - Format: LeftRightDot

**GpsPointId**:
    - Description:
    - Format: UuidCanonicalTextual

**OwnershipDeedId**:
    - Description:
    - Format: PositiveInteger

**OwnershipDeedValidatorAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**OwnerAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**DaemonAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**TradingRightsId**:
    - Description:
    - Format: PositiveInteger

**ScadaAlgoAddr**:
    - Description:
    - Format: AlgoAddressStringFormat

**ScadaCertId**:
    - Description:
    - Format: PositiveInteger

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.base_g_node_gt.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.base_g_node_gt.check_is_positive_integer
    :members:


.. autoclass:: gwbase.types.base_g_node_gt.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.base_g_node_gt.check_is_algo_address_string_format
    :members:


.. autoclass:: gwbase.types.BaseGNodeGt_Maker
    :members:
