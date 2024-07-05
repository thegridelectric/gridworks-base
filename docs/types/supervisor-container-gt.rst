SupervisorContainerGt
==========================
Python pydantic class corresponding to json type `supervisor.container.gt`, version `000`.

.. autoclass:: gwbase.types.SupervisorContainerGt
    :members:

**SupervisorContainerId**:
    - Description: Id of the docker SupervisorContainer.
    - Format: UuidCanonicalTextual

**Status**:
    - Description:

**WorldInstanceName**:
    - Description: Name of the WorldInstance.For example, d1__1 is a potential name for a World whose World GNode has alias d1.
    - Format: WorldInstanceNameFormat

**SupervisorGNodeInstanceId**:
    - Description: Id of the SupervisorContainer's prime actor (aka the Supervisor GNode).
    - Format: UuidCanonicalTextual

**SupervisorGNodeAlias**:
    - Description: Alias of the SupervisorContainer's prime actor (aka the Supervisor GNode).
    - Format: LeftRightDot

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.supervisor_container_gt.check_is_world_instance_name_format
    :members:


.. autoclass:: gwbase.types.supervisor_container_gt.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.supervisor_container_gt.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.SupervisorContainerGt_Maker
    :members:
