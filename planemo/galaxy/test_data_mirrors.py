"""Fetch remote test data from mirrors that address files by their content hash.

A mirror serves each file at ``<mirror>/<hash function>/<first 2 hex chars>/<hash value>``,
with the hash in lowercase hex, e.g.
``https://depot.galaxyproject.org/iwc-test-data/sha1/9c/9cda46eac7cbb29508975327e410f729a4f1681c``.
Remote URLs in ``tools/fetch`` payloads that carry declared ``hashes`` are pointed at
the first mirror that has a matching file, and keep their original URL if none has.
Galaxy verifies those hashes when fetching, so the mirror does not need to be
trusted. The mirror must be reachable from Galaxy, not just from planemo.
"""

import functools
import re
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

import requests

from planemo.io import info

# Galaxy hash function names, with the mirror directory and hex digest length for each,
# in order of preference
HASH_FUNCTIONS = {
    "SHA-256": ("sha256", 64),
    "SHA-512": ("sha512", 128),
    "SHA-1": ("sha1", 40),
    "MD5": ("md5", 32),
}
# (connect, read) timeouts in seconds
TIMEOUT = (3, 10)


class HashMirrors:
    """Look up remote files on mirrors by the hashes declared for them."""

    def __init__(self, mirrors: List[str], session: Optional[requests.Session] = None) -> None:
        self.mirrors = [mirror if mirror.endswith("/") else f"{mirror}/" for mirror in mirrors]
        self.session = session or requests.Session()
        self._available: Dict[str, bool] = {}
        # mirrors that could not be reached, not asked again
        self._unreachable: Set[str] = set()

    def mirror_url(self, hashes: List[Dict[str, Any]]) -> Optional[str]:
        """Return the URL of a mirror copy of the file with ``hashes``, or None if no mirror has one."""
        declared = {
            entry.get("hash_function"): str(entry.get("hash_value")).lower()
            for entry in hashes
            if isinstance(entry, dict) and entry.get("hash_value")
        }
        for function, (directory, length) in HASH_FUNCTIONS.items():
            value = declared.get(function)
            # the value becomes part of the URL, so only accept a well-formed digest
            if value is None or not re.fullmatch(f"[0-9a-f]{{{length}}}", value):
                continue
            for mirror in self.mirrors:
                url = f"{mirror}{directory}/{value[:2]}/{value}"
                if self._is_available(mirror, url):
                    return url
        return None

    def _is_available(self, mirror: str, url: str) -> bool:
        if mirror in self._unreachable:
            return False
        if url not in self._available:
            try:
                response = self.session.head(url, timeout=TIMEOUT, allow_redirects=True)
                self._available[url] = response.status_code == 200
            except requests.RequestException as e:
                info(f"Not using test data mirror {mirror}: {e}")
                self._unreachable.add(mirror)
                return False
        return self._available[url]

    def rewrite_fetch_payload(self, payload: Dict[str, Any]) -> None:
        """Point hashed remote URL elements of a ``tools/fetch`` payload at mirror copies."""
        for target in payload.get("targets") or []:
            for element in target.get("elements") or []:
                self._rewrite_element(element)

    def _rewrite_element(self, element: Dict[str, Any]) -> None:
        url = element.get("url")
        if element.get("src") != "url" or not element.get("hashes") or not isinstance(url, str):
            return
        if not url.startswith(("http://", "https://")):
            return
        mirror_url = self.mirror_url(element["hashes"])
        if mirror_url:
            info(f"Using mirror copy {mirror_url} of {url}")
            element["url"] = mirror_url


@functools.lru_cache(maxsize=None)
def hash_mirrors(mirrors: Tuple[str, ...]) -> HashMirrors:
    """Return a :class:`HashMirrors` shared by all jobs staged by this process."""
    return HashMirrors(list(mirrors))
