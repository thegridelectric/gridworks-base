GNodeInstanceGt
==========================
Python pydantic class corresponding to json type `g.node.instance.gt`, version `000`.

.. autoclass:: gwbase.types.GNodeInstanceGt
    :members:

**GNodeInstanceId**:
    - Description: Immutable identifier for GNodeInstance (Gni).
    - Format: UuidCanonicalTextual

**GNodeId**:
    - Description: The GNode represented by the Gni.
    - Format: UuidCanonicalTextual

**Strategy**:
    - Description: Used to determine the code running in a GNode actor application.

**Status**:
    - Description: Lifecycle Status for Gni.

**SupervisorContainerId**:
    - Description: The Id of the docker container where the Gni runs.
    - Format: UuidCanonicalTextual

**StartTimeUnixS**:
    - Description: When the gni starts representing the GNode.Specifically, when the Status changes from Pending to Active. Note that this is time in the GNode's World, which may not be real time if it is a simulation.
    - Format: ReasonableUnixTimeS

**EndTimeUnixS**:
    - Description: When the gni stops representing the GNode.Specifically, when the Status changes from Active to Done.

**AlgoAddress**:
    - Description: Algorand address for Gni.
    - Format: AlgoAddressStringFormat

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.g_node_instance_gt.check_is_reasonable_unix_time_s
    :members:


.. autoclass:: gwbase.types.g_node_instance_gt.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.g_node_instance_gt.check_is_algo_address_string_format
    :members:


.. autoclass:: gwbase.types.GNodeInstanceGt_Maker
    :members:
