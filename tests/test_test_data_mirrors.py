"""Unit tests for :mod:`planemo.galaxy.test_data_mirrors`."""

import os
from unittest import mock

import pytest
import requests
import responses
import yaml

from planemo.galaxy.activity import stage_in
from planemo.galaxy.test_data_mirrors import (
    hash_mirrors,
    HashMirrors,
)
from planemo.runnable import (
    Runnable,
    RunnableType,
)
from .test_utils import (
    create_test_context,
    TEST_DATA_DIR,
)

MIRROR = "https://mirror.example.org/test-data/"
SECOND_MIRROR = "https://mirror2.example.org/"
SHA1 = "9cda46eac7cbb29508975327e410f729a4f1681c"
SHA256 = "1c23617b5ec39bb5a711fa8b20fa4ab7bcb18e6fcdb8d085f1b623c773037fd8"
ORIGINAL = "https://zenodo.org/records/1/files/reads.fastq.gz?download=1"


def _file(location=ORIGINAL, **kwd):
    return {"class": "File", "location": location, **kwd}


@responses.activate
def test_mirror_url_prefers_stronger_hash_and_tries_each_mirror():
    responses.add(responses.HEAD, f"{MIRROR}sha256/{SHA256[:2]}/{SHA256}", status=404)
    responses.add(responses.HEAD, f"{SECOND_MIRROR}sha256/{SHA256[:2]}/{SHA256}", status=200)
    mirrors = HashMirrors([MIRROR.rstrip("/"), SECOND_MIRROR])
    hashes = [
        {"hash_function": "SHA-1", "hash_value": SHA1},
        {"hash_function": "SHA-256", "hash_value": SHA256.upper()},
    ]
    assert mirrors.mirror_url(hashes) == f"{SECOND_MIRROR}sha256/{SHA256[:2]}/{SHA256}"
    # cached, no further requests
    assert mirrors.mirror_url(hashes) == f"{SECOND_MIRROR}sha256/{SHA256[:2]}/{SHA256}"
    assert len(responses.calls) == 2


@responses.activate
def test_mirror_url_none_if_no_mirror_has_file():
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=404)
    responses.add(
        responses.HEAD, f"{SECOND_MIRROR}sha1/{SHA1[:2]}/{SHA1}", body=requests.ConnectionError("unreachable")
    )
    mirrors = HashMirrors([MIRROR, SECOND_MIRROR])
    assert mirrors.mirror_url([{"hash_function": "SHA-1", "hash_value": SHA1}]) is None
    assert mirrors.mirror_url([{"hash_function": "SHA-3", "hash_value": SHA1}]) is None


@responses.activate
def test_mirror_url_skips_malformed_hash_values():
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=200)
    mirrors = HashMirrors([MIRROR])
    malformed = [
        {"hash_function": "SHA-256", "hash_value": "../../" + SHA256[6:]},
        {"hash_function": "SHA-512", "hash_value": SHA256},
        {"hash_function": "SHA-1", "hash_value": f"{SHA1}\n"},
        {"hash_function": "MD5", "hash_value": "g" * 32},
    ]
    assert mirrors.mirror_url(malformed) is None
    assert len(responses.calls) == 0
    # a malformed stronger hash does not stop a well-formed weaker one from being used
    hashes = [{"hash_function": "SHA-256", "hash_value": SHA1}, {"hash_function": "SHA-1", "hash_value": SHA1}]
    assert mirrors.mirror_url(hashes) == f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}"
    assert len(responses.calls) == 1


@responses.activate
def test_unreachable_mirror_is_not_asked_again():
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", body=requests.ConnectionError("unreachable"))
    mirrors = HashMirrors([MIRROR])
    assert mirrors.mirror_url([{"hash_function": "SHA-1", "hash_value": SHA1}]) is None
    assert mirrors.mirror_url([{"hash_function": "SHA-256", "hash_value": SHA256}]) is None
    assert len(responses.calls) == 1


@responses.activate
def test_mirror_is_asked_again_after_read_timeout():
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", body=requests.ReadTimeout("slow"))
    responses.add(responses.HEAD, f"{MIRROR}sha256/{SHA256[:2]}/{SHA256}", status=200)
    mirrors = HashMirrors([MIRROR])
    assert mirrors.mirror_url([{"hash_function": "SHA-1", "hash_value": SHA1}]) is None
    assert mirrors.mirror_url([{"hash_function": "SHA-256", "hash_value": SHA256}]) == (
        f"{MIRROR}sha256/{SHA256[:2]}/{SHA256}"
    )


@responses.activate
def test_rewrite_fetch_payload():
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=200)
    hashes = [{"hash_function": "SHA-1", "hash_value": SHA1}]
    elements = [
        {"src": "url", "url": ORIGINAL, "hashes": hashes, "name": "reads"},
        {"src": "url", "url": ORIGINAL},
        {"src": "url", "url": "file:///data/reads.fastq.gz", "hashes": hashes},
        {"src": "files", "hashes": hashes},
        {"src": "composite", "hashes": hashes, "composite": {"items": [{"src": "url", "url": ORIGINAL}]}},
    ]
    payload = {"targets": [{"elements": [dict(element) for element in elements]}]}
    HashMirrors([MIRROR]).rewrite_fetch_payload(payload)
    rewritten = payload["targets"][0]["elements"]
    assert rewritten[0] == {**elements[0], "url": f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}"}
    assert rewritten[1:] == elements[1:]


@pytest.fixture(autouse=True)
def clear_hash_mirrors():
    hash_mirrors.cache_clear()


def _stage(tmp_path, job, version_major="26.0", **kwds):
    """Stage ``job`` with the real staging interface, returning the ``(api_path, payload)`` pairs posted."""
    posted = []

    def make_post_request(url, payload=None, files_attached=False):
        api_path = url.split("/api/", 1)[1]
        posted.append((api_path, payload))
        if api_path == "dataset_collections":
            return {"id": f"hdca{len(posted)}"}
        return {"outputs": [{"id": f"hda{len(posted)}", "hid": len(posted)}], "jobs": []}

    config = mock.MagicMock(version_major=version_major, use_path_paste=False)
    config.user_gi.url = "http://galaxy.example.org/"
    config.user_gi.make_post_request.side_effect = make_post_request
    job_path = tmp_path / "job.yml"
    job_path.write_text(yaml.safe_dump(job, sort_keys=False))
    runnable = Runnable(os.path.join(TEST_DATA_DIR, "wf2.ga"), RunnableType.galaxy_workflow)
    stage_in(create_test_context(), runnable, config, str(job_path), history_id="historyid123", **kwds)
    return posted


def _fetch_elements(posted):
    return [payload["targets"][0]["elements"][0] for api_path, payload in posted if api_path == "tools/fetch"]


@responses.activate
def test_stage_in_fetches_mirror_copy_with_declared_hashes(tmp_path):
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=200)
    hashes = [{"hash_function": "SHA-1", "hash_value": SHA1}]
    job = {
        "reads": _file(hashes=hashes),
        "list": [_file(hashes=hashes)],
        "collection": {
            "class": "Collection",
            "collection_type": "list:paired",
            "elements": [
                {
                    "class": "Collection",
                    "type": "paired",
                    "identifier": "sample1",
                    "elements": [
                        _file(identifier="forward", hashes=hashes),
                        _file(identifier="reverse", hashes=hashes),
                    ],
                }
            ],
        },
        "record": {"reads": _file(hashes=hashes)},
        "composite": _file(hashes=hashes, composite_data=[ORIGINAL]),
    }
    elements = _fetch_elements(_stage(tmp_path, job, test_data_mirror=(MIRROR,)))
    assert len(elements) == 6
    for element in elements[:4]:
        assert element["src"] == "url"
        assert element["url"] == f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}"
        assert element["hashes"] == hashes
        assert element["name"] == "reads.fastq.gz?download=1"
    # staged without hashes, so Galaxy could not verify a mirror copy
    assert elements[4]["url"] == ORIGINAL
    assert "hashes" not in elements[4]
    assert elements[5]["src"] == "composite"
    assert elements[5]["composite"]["items"] == [{"src": "url", "url": ORIGINAL}]


@responses.activate
def test_stage_in_legacy_upload_does_not_use_mirror(tmp_path):
    # the legacy upload API does not send hashes, so Galaxy would not verify a mirror copy
    responses.add(responses.HEAD, f"{MIRROR}sha256/{SHA256[:2]}/{SHA256}", status=200)
    job = {"input": _file(hashes=[{"hash_function": "SHA-256", "hash_value": SHA256}])}
    posted = _stage(tmp_path, job, version_major="20.05", test_data_mirror=(MIRROR,))
    assert [api_path for api_path, _ in posted] == ["tools"]
    assert posted[0][1]["inputs"]["files_0|url_paste"] == ORIGINAL
    assert len(responses.calls) == 0


@responses.activate
def test_stage_in_without_mirror_fetches_original(tmp_path):
    responses.add(responses.HEAD, f"{MIRROR}sha256/{SHA256[:2]}/{SHA256}", status=200)
    job = {"input": _file(hashes=[{"hash_function": "SHA-256", "hash_value": SHA256}])}
    elements = _fetch_elements(_stage(tmp_path, job))
    assert [element["url"] for element in elements] == [ORIGINAL]
    assert len(responses.calls) == 0


@responses.activate
def test_stage_in_uses_mirror_for_nested_element_without_class(tmp_path):
    # galaxy-tool-util nests collection elements by collection_type, not class
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=200)
    hashes = [{"hash_function": "SHA-1", "hash_value": SHA1}]
    job = {
        "collection": {
            "class": "Collection",
            "collection_type": "list:list",
            "elements": [{"identifier": "outer", "elements": [_file(identifier="inner", hashes=hashes)]}],
        }
    }
    elements = _fetch_elements(_stage(tmp_path, job, test_data_mirror=(MIRROR,)))
    assert [element["url"] for element in elements] == [f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}"]


@responses.activate
def test_stage_in_does_not_look_up_existing_datasets(tmp_path):
    responses.add(responses.HEAD, f"{MIRROR}sha1/{SHA1[:2]}/{SHA1}", status=200)
    job = {"input": _file(galaxy_id="abc123", hashes=[{"hash_function": "SHA-1", "hash_value": SHA1}])}
    assert _stage(tmp_path, job, test_data_mirror=(MIRROR,)) == []
    assert len(responses.calls) == 0
