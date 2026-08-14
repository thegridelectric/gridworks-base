"""Pika credentials for the GridWorks SASL mechanism.

The broker's GridWorks mechanism takes a connection's identity from its TLS
client certificate and treats the SASL response bytes as a claims payload,
which it forwards to the Fleet Index Service (FIS) for the authorization
decision. So this class carries no secret: the private key proving identity
lives in the TLS layer, and what travels in the SASL response is a
``fis.connect.claims`` word stating which alias, process instance, and run
the connecting process believes it is.

Two consequences worth holding onto. A claims-bearing connect can only be
completed by the holder of the certificate's private key, so a forged
instance claim requires key theft rather than guesswork. And because the
payload is a Sema word rather than an ad-hoc string, evolving what a
principal claims is a word version on both sides, not a broker change.
"""

import pika
from pika.compat import as_bytes
from pika.spec import Connection

from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import FisConnectClaims

_CODEC = GwBaseSemaCodec()


class GridworksClaimsCredentials:
    """Advertises the ``GRIDWORKS`` mechanism and answers with the claims.

    Construct with the claims this process asserts; pass the instance as
    ``credentials`` on any pika connection parameters.
    """

    TYPE = "GRIDWORKS"

    def __init__(self, claims: FisConnectClaims) -> None:
        self.claims = claims
        # Pika erases credentials after connecting when this is set. There is
        # nothing secret to erase here, and the claims stay readable for
        # reconnects and for logging what this process asserted.
        self.erase_on_connect = False

    def response_for(self, start: Connection.Start) -> tuple[str | None, bytes | None]:
        """Return the mechanism name and the claims payload, or (None, None)
        when the broker does not offer the GridWorks mechanism.

        Answering (None, None) is how pika learns to try another credentials
        type, so a broker that has not been switched over yet fails as an
        ordinary auth negotiation rather than a crash.
        """
        if as_bytes(self.TYPE) not in as_bytes(start.mechanisms).split():
            return None, None
        return self.TYPE, _CODEC.to_bytes(self.claims)

    def erase_credentials(self) -> None:
        """Nothing to erase — see ``erase_on_connect``."""


# Pika validates a connection's credentials object against this list, so
# registering here is the supported way to add a mechanism. Guarded because
# importing a module twice under different names must not double-register.
if GridworksClaimsCredentials not in pika.credentials.VALID_TYPES:
    pika.credentials.VALID_TYPES.append(GridworksClaimsCredentials)
