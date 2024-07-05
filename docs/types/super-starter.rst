SuperStarter
==========================
Python pydantic class corresponding to json type `super.starter`, version `000`.

.. autoclass:: gwbase.types.SuperStarter
    :members:

**SupervisorContainer**:
    - Description: Key data about the docker container.

**GniList**:
    - Description: List of GNodeInstances (Gnis) run in the container.

**AliasWithKeyList**:
    - Description: Aliases of Gnis that own Algorand secret keys.
    - Format: LeftRightDot

**KeyList**:
    - Description: Algorand secret keys owned by Gnis.

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.super_starter.check_is_left_right_dot
    :members:


.. autoclass:: gwbase.types.SuperStarter_Maker
    :members:
