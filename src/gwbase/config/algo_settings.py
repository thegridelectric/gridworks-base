from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Public(BaseModel):
    """
    Publicly available information about the GNodeFactory, including:
      - GnfAdminAddr
      - GnfApiRoot
      - TaValidatorFundingThresholdAlgos
      - TaDeedConsiderationAlgos

    Also includes useful information shartcuts for running the simulated Millinocket
    demo. In this demo there is only one MarketMaker, and one TaValidator.
    Public Algorand addresses and ApiRoots are included for both.
    """

    gnf_api_root: str = "http://localhost:8000"
    dev_market_maker_api_root: str = "http://localhost:7997"
    dev_ta_validator_api_root: str = "http://localhost:8001"
    gnf_admin_addr: str = "RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI"
    gnr_addr: str = "X2ASUAUPK5ICMGDXQZQKBPSXWEJLBA4KKQ2TXW2KWO2JQTLY3J2Q4S33WE"
    dev_market_maker_addr: str = (
        "JMEUH2AXM6UGRJO2DBZXDOA2OMIWQFNQZ54LCVC4GQX6QDOX5Z6JRGMWFA"
    )
    dev_ta_validator_addr: str = (
        "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII"
    )
    dev_ta_validator_multi_addr: str = (
        "Y5TRQXIJHWJ4OHCZSWP4PZTCES5VWOF2KDTNYSMU5HLAUXBFQQDX6IR5KM'"
    )
    ta_validator_funding_threshold_algos: int = 100
    ta_deed_consideration_algos: int = 50
    universe: str = "dev"
    gnf_graveyard_addr: str = (
        "COA6SYUOBE33F5JDYEGC5XAD43QRG3VGHNNQXLYWFSSQEHDQ5HJ52NDNPI"
    )
    algod_address: str = "http://localhost:4001"
    kmd_address: str = "http://localhost:4002"
    gen_kmd_wallet_name: str = "unencrypted-default-wallet"


class AlgoApiSecrets(BaseModel):
    algod_token: SecretStr = SecretStr(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )
    kmd_token: SecretStr = SecretStr(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )
    gen_kmd_wallet_password: SecretStr = SecretStr("")


class VanillaSettings(BaseSettings):
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    public: Public = Public()

    model_config = SettingsConfigDict(
        env_prefix="VANILLA_", env_nested_delimiter="__", extra="ignore"
    )
