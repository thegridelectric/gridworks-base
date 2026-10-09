"""The identity a gwbase process connects to the broker as."""

from urllib.parse import urlparse

from cryptography import x509
from cryptography.x509.oid import NameOID

from gwbase.config.rabbit_settings import RabbitBrokerClient


def principal_id(rabbit: RabbitBrokerClient) -> str:
    """The username the broker authenticates this process as.

    With a ``tls`` block the identity is the client certificate's subject CN
    (the principal id: a GNodeId for a GNode, a uuid4 for a platform
    service), which the broker derives at the handshake. Without one it is
    the URL's username. Every publish carries this as ``user_id`` so the
    broker's validated-user-id check has something to compare with the
    authenticated name.
    """
    if rabbit.tls is not None:
        cert = x509.load_pem_x509_certificate(rabbit.tls.cert_path.read_bytes())
        cns = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if len(cns) != 1:
            raise ValueError(
                f"{rabbit.tls.cert_path}: expected one subject CN, found {len(cns)}"
            )
        value = cns[0].value
        return value if isinstance(value, str) else value.decode()
    username = urlparse(rabbit.url.get_secret_value()).username
    if not username:
        raise ValueError("rabbit.url carries no username and rabbit.tls is unset")
    return username
