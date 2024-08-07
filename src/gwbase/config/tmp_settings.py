from pydantic_settings import BaseSettings

DEFAULT_ENV_FILE = ".env"


class EnumSettings(BaseSettings):
    encode: int = 1  # use  8-digit hex encoded enum symbol if 1; send enum value if 0

    class Config:
        env_prefix = "ENUM_"
        env_nested_delimiter = "__"


class GNodeSettings(BaseSettings):
    """
    Template settings for a GNode.
    """

    g_node_alias: str = "d1.isone.unknown.gnode"

    class Config:
        env_prefix = "GNODE_"
        env_nested_delimiter = "__"
