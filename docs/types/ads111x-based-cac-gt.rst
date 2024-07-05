Ads111xBasedCacGt
==========================
Python pydantic class corresponding to json type `ads111x.based.cac.gt`, version `000`.

.. autoclass:: gwbase.types.Ads111xBasedCacGt
    :members:

**ComponentAttributeClassId**:
    - Description: ComponentAttributeClassId.Unique identifier for the device class (aka 'cac' or Component Attribute Class). Authority is maintained by the World Registry.
    - Format: UuidCanonicalTextual

**MinPollPeriodMs**:
    - Description: Min Poll Period in Milliseconds.Poll Period refers to the period of time between two readings by the local actor. This is in contrast to Capture Period, which refers to the period between readings that are sent up to the cloud (or otherwise saved for the long-term).
    - Format: PositiveInteger

**MakeModel**:
    - Description: MakeModel.Meant to be enough to articulate any difference in how GridWorks code would interact with a device. Should be able to use this information to buy or build a device.

**AdsI2cAddressList**:
    - Description: Ads I2c Address List.The list of I2C Addresses for the Texas Instrument Ads111X chips comprising this device.
    - Format: Ads1115I2cAddress

**TotalTerminalBlocks**:
    - Description: Total Thermistor Channels.There are at most 4 thermisters per Ads111X chip. The channels always start with the number 1, and the channels are expected to follow the natural enumeration set by the AdsI2cAddressList and the associated AI0 through AI3 on those chips. Analog In 3 on the final chip may be reserved for calculating a reference open voltage. The total number of channels may also be constrained by the screw terminal situation.
    - Format: PositiveInteger

**TelemetryNameList**:
    - Description: Telemetry Name List.The list of TelemetryNames that this device/driver combination is capable of producing.

**DisplayName**:
    - Description: Display Name.Sample: GridWorks TSnap1.0 as 12-channel analog temp sensor

**TypeName**:
    - Description: All GridWorks Versioned Types have a fixed TypeName, which is a string of lowercase alphanumeric words separated by periods, most significant word (on the left) starting with an alphabet character, and final word NOT all Hindu-Arabic numerals.

**Version**:
    - Description: All GridWorks Versioned Types have a fixed version, which is a string of three Hindu-Arabic numerals.



.. autoclass:: gwbase.types.ads111x_based_cac_gt.check_is_uuid_canonical_textual
    :members:


.. autoclass:: gwbase.types.ads111x_based_cac_gt.check_is_ads1115_i2c_address
    :members:


.. autoclass:: gwbase.types.ads111x_based_cac_gt.check_is_positive_integer
    :members:


.. autoclass:: gwbase.types.Ads111xBasedCacGt_Maker
    :members:
