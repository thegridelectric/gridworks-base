"""Invariants for the RabbitMQ definitions builder."""

import base64
import hashlib

from gwbase import topology
from gwbase.rabbit_definitions import build_definitions, rabbit_password_hash


def test_password_hash_matches_rabbit_algorithm() -> None:
    # rabbit_password_hashing_sha256: base64(salt ++ sha256(salt ++ pw))
    h = rabbit_password_hash("smqPublic")
    raw = base64.b64decode(h)
    salt, digest = raw[:4], raw[4:]
    assert digest == hashlib.sha256(salt + b"smqPublic").digest()
    # deterministic (fixed salt) so CI can diff
    assert rabbit_password_hash("smqPublic") == h


def test_dev_definitions_include_user_and_permissions() -> None:
    d = build_definitions(vhost="d1__1", user="smqPublic", password="smqPublic")
    assert d["vhosts"] == [{"name": "d1__1"}]
    assert len(d["users"]) == 1
    assert d["users"][0]["name"] == "smqPublic"
    assert d["users"][0]["hashing_algorithm"] == "rabbit_password_hashing_sha256"
    assert "administrator" in d["users"][0]["tags"]
    assert d["permissions"] == [
        {"user": "smqPublic", "vhost": "d1__1",
         "configure": ".*", "write": ".*", "read": ".*"}
    ]


def test_prod_definitions_have_no_baked_credential() -> None:
    d = build_definitions(vhost="hw1__1")
    assert d["vhosts"] == [{"name": "hw1__1"}]
    assert d["users"] == []
    assert d["permissions"] == []


def test_exchanges_and_bindings_track_topology() -> None:
    d = build_definitions(vhost="d1__1")
    assert len(d["exchanges"]) == len(topology.exchanges())
    assert len(d["bindings"]) == len(topology.exchange_bindings())

    by_name = {e["name"]: e for e in d["exchanges"]}
    assert by_name["ear_tx"]["internal"] is True
    assert by_name["ltn_tx"]["internal"] is True
    assert by_name["ltnmic_tx"]["internal"] is False
    # every exchange/binding is scoped to the vhost, topic, durable
    assert all(e["vhost"] == "d1__1" and e["type"] == "topic" for e in d["exchanges"])
    assert all(b["vhost"] == "d1__1" for b in d["bindings"])

    # a known direct edge and the amq.topic ear tap survive into the JSON
    assert any(
        b["source"] == "ltnmic_tx" and b["destination"] == "super_tx"
        and b["routing_key"] == "*.*.ltn.*.super.*"
        for b in d["bindings"]
    )
    assert any(
        b["source"] == "amq.topic" and b["destination"] == "ear_tx"
        and b["routing_key"] == "#"
        for b in d["bindings"]
    )
