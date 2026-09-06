import base64
import ctypes
import os
import sys
from ctypes import wintypes

from cryptography.hazmat.primitives import serialization
from cryptography.x509 import BasicConstraints, ExtensionOID, load_der_x509_certificate


class _CERT_CONTEXT(ctypes.Structure):
    _fields_ = [
        ("dwCertEncodingType", wintypes.DWORD),
        ("pbCertEncoded", wintypes.PBYTE),
        ("cbCertEncoded", wintypes.DWORD),
        ("pCertInfo", ctypes.c_void_p),
        ("hCertStore", ctypes.c_void_p),
    ]


_PCCERT_CONTEXT = ctypes.POINTER(_CERT_CONTEXT)
_crypt32 = ctypes.windll.crypt32

_CertOpenSystemStoreW = _crypt32.CertOpenSystemStoreW
_CertOpenSystemStoreW.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR]
_CertOpenSystemStoreW.restype = wintypes.HANDLE

_CertEnumCertificatesInStore = _crypt32.CertEnumCertificatesInStore
_CertEnumCertificatesInStore.argtypes = [wintypes.HANDLE, _PCCERT_CONTEXT]
_CertEnumCertificatesInStore.restype = _PCCERT_CONTEXT

_CertCloseStore = _crypt32.CertCloseStore
_CertCloseStore.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_CertCloseStore.restype = wintypes.BOOL


def _export_store(name: str) -> list[bytes]:
    store = _CertOpenSystemStoreW(None, name)
    if not store:
        return []
    certs: list[bytes] = []
    ctx: _PCCERT_CONTEXT | None = None
    while True:
        ctx = _CertEnumCertificatesInStore(store, ctx)
        if not ctx:
            break
        cb = ctx.contents.cbCertEncoded
        pb = ctx.contents.pbCertEncoded
        certs.append(bytes(pb[:cb]))
    _CertCloseStore(store, 0)
    return certs


def _is_trusted_ca(cert) -> bool:
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        bc: BasicConstraints = ext.value
        return bool(bc.ca and ext.critical)
    except Exception:
        return False


def _to_pem(der: bytes) -> str | None:
    try:
        cert = load_der_x509_certificate(der)
        if not _is_trusted_ca(cert):
            return None
        return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    except Exception:
        return None


def main() -> int:
    bundle_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(os.path.dirname(__file__), "ca-bundle.pem")
    )
    pems: list[str] = []
    for store_name in ("ROOT", "CA", "AuthRoot"):
        for der in _export_store(store_name):
            pem = _to_pem(der)
            if pem:
                pems.append(pem)
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write("".join(pems))
    print(bundle_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
