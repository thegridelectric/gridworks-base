import algosdk

from gwbase.enums import UniverseType


def check_is_algo_secret_key_format(v: str) -> None:
    try:
        algosdk.account.address_from_private_key(v)
    except Exception as e:
        raise ValueError(
            f"Not Algorand Secret Key format! Generate one by: \n"
            f"import algosdk\n"
            "private_key, address = algosdk.account.generate_account()\n"
            f"incorrect sk: {v}",
        ) from e


def check_is_left_right_dot(v: str) -> None:
    """
    LeftRightDot format: Lowercase alphanumeric words separated by periods,
    most significant word (on the left) starting with an alphabet character.

    Raises:
        ValueError: if not LeftRightDot format
    """
    from typing import List

    try:
        x: List[str] = v.split(".")
    except Exception as e:
        raise ValueError(f"Failed to seperate {v} into words with split'.'") from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(f"Most significant word of {v} must start with alphabet char.")
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of {v} split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of {v} must be lowercase.")


def check_is_reasonable_unix_time_s(v: int) -> None:
    """
    ReasonableUnixTimeS format: time in unix seconds between Jan 1 2000 and Jan 1 3000

    Raises:
        ValueError: if not ReasonableUnixTimeS format
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


def check_g_node_alias(alias: str, universe_type: UniverseType) -> None:
    check_is_left_right_dot(alias)
    first_word = alias.split(".")[0]
    if universe_type == UniverseType.Dev:
        if not first_word.startswith("d"):
            raise ValueError(
                f"Bad alias {alias} ... Dev universe GNode alias must start with d.",
            )
    elif universe_type == UniverseType.Hybrid:
        if not first_word.startswith("h"):
            raise ValueError(
                f"Bad alias {alias} ... Hybrid universe GNode alias must start with h.",
            )
    elif universe_type == UniverseType.Production:
        if not first_word == "w":
            raise ValueError(
                f"Bad alias {alias} ... Production universe GNode alias must have w as first word.",
            )
