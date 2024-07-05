SimTimestep
==========================
Python pydantic class corresponding to json type `sim.timestep`, version `000`.

.. autoclass:: gwbase.types.SimTimestep
    :members:

**FromGNodeAlias**:
    - Description: The GNodeAlias of the sender.The sender should always be a GNode Actor of role TimeCoordinator.
    - Format: LeftRightDot

**FromGNodeInstanceId**:
    - Description: The GNodeInstanceId of the sender.
    - Format: UuidCanonicalTextual

**TimeUnixS**:
    - Description: Current time in unix seconds.
    - Format: ReasonableUnixTimeS

**TimestepCreatedMs**:
    - Description: The real time created, in unix milliseconds.
    - Format: ReasonableUnixTimeMs

**MessageId**:
    - Description: MessageId.
    - Format: UuidCanonicalTextual

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.sim_timestep.check_is_reasonable_unix_time_s
    :members:


.. autoclass:: gwbase.types.sim_timestep.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.sim_timestep.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.sim_timestep.check_is_reasonable_unix_time_ms
    :members:


.. autoclass:: gwbase.types.SimTimestep_Maker
    :members:
