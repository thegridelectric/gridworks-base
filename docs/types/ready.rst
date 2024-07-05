Ready
==========================
Python pydantic class corresponding to json type `ready`, version `001`.

.. autoclass:: gwbase.types.Ready
    :members:

**FromGNodeAlias**:
    - Description: The GNodeAlias of the sender.
    - Format: LeftRightDot

**FromGNodeInstanceId**:
    - Description: The GNodeInstanceId of the sender.
    - Format: UuidCanonicalTextual

**TimeUnixS**:
    - Description: Latest simulated time for sender.The time in unix seconds of the latest TimeStep received from the TimeCoordinator by the actor that sent the payload.

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.ready.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.ready.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.Ready_Maker
    :members:
