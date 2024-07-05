HeartbeatA
==========================
Python pydantic class corresponding to json type `heartbeat.a`, version `100`.

.. autoclass:: gwbase.types.HeartbeatA
    :members:

**MyHex**:
    - Description: Hex character getting sent.
    - Format: HexChar

**YourLastHex**:
    - Description: Last hex character received from heartbeat partner.
    - Format: HexChar

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.heartbeat_a.check_is_hex_char
    :members:


.. autoclass:: gwbase.types.HeartbeatA_Maker
    :members:
