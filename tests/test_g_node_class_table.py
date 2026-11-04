"""The GNode-class to transport-class table is the tier map in code: every
GridWorks GNode class but Unknown has one transport class, no two share
one, and a GNode actor cannot claim a class off the table."""

from gwbase.sema.enums import GwGNodeClass
from gwbase.transport_encoding import TRANSPORT_CLASS_BY_G_NODE_CLASS, TransportClass


def test_every_g_node_class_but_unknown_has_a_transport_class() -> None:
    assert set(TRANSPORT_CLASS_BY_G_NODE_CLASS) == set(GwGNodeClass) - {
        GwGNodeClass.Unknown
    }


def test_the_table_is_injective() -> None:
    values = list(TRANSPORT_CLASS_BY_G_NODE_CLASS.values())
    assert len(values) == len(set(values))


def test_the_non_gnode_transport_classes_stay_off_the_table() -> None:
    off = set(TransportClass) - set(TRANSPORT_CLASS_BY_G_NODE_CLASS.values())
    assert off == {
        TransportClass.Supervisor,
        TransportClass.GridNodeRegistry,
        TransportClass.Alerter,
    }
