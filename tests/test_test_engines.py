import os

from planemo.engine.test import (
    test_runnables as t_runnables
)
from planemo.runnable import (
    for_paths,
)
from .test_utils import (
    mark,
    PROJECT_TEMPLATES_DIR,
    skip_if_environ,
    skip_unless_module,
    target_galaxy_branch,
    test_context as t_context,
    TEST_DATA_DIR,
)


@skip_if_environ("PLANEMO_SKIP_CWLTOOL_TESTS")
@skip_unless_module("toil")
def test_toil_tests():
    ctx = t_context()
    test_artifact = os.path.join(TEST_DATA_DIR, "int_tool.cwl")
    runnables = for_paths([test_artifact])
    exit_code = t_runnables(
        ctx,
        runnables,
        engine="toil",
    )
    assert exit_code == 0


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
@mark.tests_galaxy_branch
def test_galaxy_wf_tests():
    ctx = t_context()
    random_lines = os.path.join(PROJECT_TEMPLATES_DIR, "demo", "randomlines.xml")
    cat = os.path.join(PROJECT_TEMPLATES_DIR, "demo", "cat.xml")
    test_artifact = os.path.join(TEST_DATA_DIR, "wf1.gxwf.yml")
    runnables = for_paths([test_artifact])
    kwds = {
        "engine": "galaxy",
        "no_dependency_resolution": True,
        "paste_test_data_paths": False,
        "galaxy_branch": target_galaxy_branch(),
        "extra_tools": [random_lines, cat]
    }
    exit_code = t_runnables(
        ctx,
        runnables,
        **kwds
    )
    assert exit_code == 0


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
@mark.tests_galaxy_branch
def test_galaxy_workflow_collection_output():
    ctx = t_context()
    test_artifact = os.path.join(TEST_DATA_DIR, "wf7-collection-output.gxwf.yml")
    collection_creates_pair = os.path.join(TEST_DATA_DIR, "collection_creates_pair_2.xml")
    runnables = for_paths([test_artifact])
    kwds = {
        "engine": "galaxy",
        "no_dependency_resolution": True,
        "paste_test_data_paths": False,
        "galaxy_branch": target_galaxy_branch(),
        "extra_tools": [collection_creates_pair],
    }
    exit_code = t_runnables(
        ctx,
        runnables,
        **kwds
    )
    assert exit_code == 0


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
@mark.tests_galaxy_branch
def test_galaxy_workflow_collection_output_fail():
    ctx = t_context()
    test_artifact = os.path.join(TEST_DATA_DIR, "wf7-collection-output-fail.gxwf.yml")
    collection_creates_pair = os.path.join(TEST_DATA_DIR, "collection_creates_pair_2.xml")
    runnables = for_paths([test_artifact])
    kwds = {
        "engine": "galaxy",
        "no_dependency_resolution": True,
        "paste_test_data_paths": False,
        "galaxy_branch": target_galaxy_branch(),
        "extra_tools": [collection_creates_pair],
    }
    exit_code = t_runnables(
        ctx,
        runnables,
        **kwds
    )
    assert exit_code == 1


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
@mark.tests_galaxy_branch
def test_galaxy_workflow_tags():
    with NamedTemporaryFile(prefix="data_manager_test_json") as json_out:
        ctx = t_context()
        test_artifact = os.path.join(TEST_DATA_DIR, "wf10-tags-and-rules.gxwf.yml")
        collection_cat_list = os.path.join(TEST_DATA_DIR, "cat_list.xml")
        runnables = for_paths([test_artifact])
        kwds = {
            "engine": "galaxy",
            "no_dependency_resolution": True,
            "paste_test_data_paths": False,
            "galaxy_branch": target_galaxy_branch(),
            "extra_tools": [collection_cat_list],
            "test_output_json": json_out.name
        }
        try:
            exit_code = t_runnables(
                ctx,
                runnables,
                **kwds
            )
            assert exit_code == 0
        except Exception:
            with open(json_out.name, "r") as f:
                print(f.read())
            raise


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
@mark.tests_galaxy_branch
def test_galaxy_workflow_nested_collection_inputs():
    ctx = t_context()
    test_artifact = os.path.join(TEST_DATA_DIR, "wf8-collection-nested-input.gxwf.yml")
    collection_cat_pair = os.path.join(TEST_DATA_DIR, "cat_pair.xml")
    collection_cat_list = os.path.join(TEST_DATA_DIR, "cat_list.xml")
    runnables = for_paths([test_artifact])
    kwds = {
        "engine": "galaxy",
        "no_dependency_resolution": True,
        "paste_test_data_paths": False,
        "galaxy_branch": target_galaxy_branch(),
        "extra_tools": [collection_cat_pair, collection_cat_list],
    }
    exit_code = t_runnables(
        ctx,
        runnables,
        **kwds
    )
    assert exit_code == 0
