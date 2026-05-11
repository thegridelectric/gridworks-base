from enum import StrEnum
from gwbase.enums import GNodeClass



class RoutingClass(StrEnum):
    # domain-backed
    TerminalAsset = "ta"
    ConnectivityNode = "cn"
    LeafTransactiveNode = "ltn"
    MarketMaker = "mm"
    Scada = "scada"
    PriceForecastService = "price"
    WeatherForecastService = "weather"
    TimeCoordinator = "time"
    # control plane
    Supervisor = "super"



ROUTING_CLASS_BY_GNODE_CLASS: dict[GNodeClass, RoutingClass] = {
    GNodeClass.TerminalAsset: RoutingClass.TerminalAsset,
    GNodeClass.ConnectivityNode: RoutingClass.ConnectivityNode,
    GNodeClass.LeafTransactiveNode: RoutingClass.LeafTransactiveNode,
    GNodeClass.MarketMaker: RoutingClass.MarketMaker,
    GNodeClass.Scada: RoutingClass.Scada,
    GNodeClass.PriceForecastService: RoutingClass.PriceForecastService,
    GNodeClass.WeatherForecastService: RoutingClass.WeatherForecastService,
    GNodeClass.TimeCoordinator: RoutingClass.TimeCoordinator,
}

class MessageCategory(StrEnum):
    """Defines routing + envelope structure."""
    JsonDirect = "rj"
    JsonBroadcast = "rjb"
    Wrapped = "gw"
    Serial = "s"  # reserved


class PayloadEncoding(StrEnum):
    """Defines how payload bytes are encoded."""
    Json = "json"
    Binary = "binary"
