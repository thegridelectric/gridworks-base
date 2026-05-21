"""Render a RabbitMQ management-plugin *definitions* JSON from the shared
topology source (`gwbase.topology`).

The broker loads this via ``management.load_definitions`` (dev/prod), and
``tests/_stubs.py`` provisions the *same* topology at runtime — both derive
from `gwbase.topology`, so they cannot diverge. See
``wiki/gridworks-base/executor/provisioning.md`` §3.6.

Output is deterministic (fixed salt, sorted keys) so a CI guard can
regenerate-and-diff against the committed artifacts.
"""

import base64
import hashlib
from typing import Any

from gwbase import topology

# Fixed 4-byte salt so the dev password hash is deterministic (the dev
# credential is non-secret; determinism is what lets CI diff the output).
_DEV_SALT = b"\x1a\x2b\x3c\x4d"


def rabbit_password_hash(password: str, *, salt: bytes = _DEV_SALT) -> str:
    """RabbitMQ ``rabbit_password_hashing_sha256`` hash:
    ``base64(salt ++ sha256(salt ++ password))``.

    NOTE: only for the **non-secret dev** credential. Prod users/passwords
    are injected at deploy, never baked into a committed artifact.
    """
    digest = hashlib.sha256(salt + password.encode("utf-8")).digest()
    return base64.b64encode(salt + digest).decode("ascii")


def build_definitions(
    *,
    vhost: str,
    user: str | None = None,
    password: str | None = None,
) -> dict[str, Any]:
    """Build the management-plugin definitions dict for one vhost.

    Exchanges and bindings come from `gwbase.topology`. If ``user`` is
    given, a single administrator user (with a deterministic dev password
    hash) and full permissions on the vhost are included — use this for
    **dev** only. Omit ``user`` for **prod**: the vhost + fabric are
    defined, but the user/permissions are provisioned out-of-band so no
    credential is baked into the artifact.
    """
    definitions: dict[str, Any] = {
        "vhosts": [{"name": vhost}],
        "users": [],
        "permissions": [],
        "topic_permissions": [],
        "parameters": [],
        "global_parameters": [],
        "policies": [],
        "queues": [],
        "exchanges": [
            {
                "name": ex.name,
                "vhost": vhost,
                "type": ex.exchange_type,
                "durable": ex.durable,
                "auto_delete": False,
                "internal": ex.internal,
                "arguments": {},
            }
            for ex in topology.exchanges()
        ],
        "bindings": [
            {
                "source": b.source,
                "vhost": vhost,
                "destination": b.destination,
                "destination_type": "exchange",
                "routing_key": b.routing_key,
                "arguments": {},
            }
            for b in topology.exchange_bindings()
        ],
    }

    if user is not None:
        definitions["users"] = [
            {
                "name": user,
                "password_hash": rabbit_password_hash(password or user),
                "hashing_algorithm": "rabbit_password_hashing_sha256",
                "tags": ["administrator"],
            }
        ]
        definitions["permissions"] = [
            {
                "user": user,
                "vhost": vhost,
                "configure": ".*",
                "write": ".*",
                "read": ".*",
            }
        ]

    return definitions
