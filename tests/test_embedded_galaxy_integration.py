"""Opt-in integration coverage for package-installed embedded Galaxy.

Run with ``PLANEMO_TEST_EMBEDDED_GALAXY=1`` in an environment containing a
Galaxy build with galaxyproject/galaxy#23360.
"""

import json
import os
import threading
from dataclasses import replace
from unittest.mock import patch

from .test_utils import (
    CliTestCase,
    PROJECT_TEMPLATES_DIR,
    skip_unless_environ,
    TEST_DATA_DIR,
    TEST_TOOLS_DIR,
)


class EmbeddedGalaxyIntegrationTestCase(CliTestCase):
    @skip_unless_environ("PLANEMO_TEST_EMBEDDED_GALAXY")
    def test_tools_upload_and_workflow_share_one_embedded_application(self):
        xml_tool_path = os.path.join(PROJECT_TEMPLATES_DIR, "demo", "cat.xml")
        yaml_tool_path = os.path.join(TEST_TOOLS_DIR, "embedded_echo.yml")
        workflow_path = os.path.join(TEST_DATA_DIR, "wf2.ga")

        from planemo.galaxy import embedded

        load_runtime_dependencies = embedded._load_runtime_dependencies
        construction_count = 0

        def load_counted_runtime_dependencies():
            dependencies = load_runtime_dependencies()
            build_galaxy_web_app = dependencies.build_galaxy_web_app

            def counted_build(*args, **kwds):
                nonlocal construction_count
                construction_count += 1
                return build_galaxy_web_app(*args, **kwds)

            return replace(dependencies, build_galaxy_web_app=counted_build)

        with self._isolate() as test_directory:
            report_path = os.path.join(test_directory, "embedded-report.json")
            with patch.object(embedded, "_load_runtime_dependencies", load_counted_runtime_dependencies):
                result = self._check_exit_code(
                    [
                        "test",
                        "--engine",
                        "embedded_galaxy",
                        "--no_dependency_resolution",
                        "--test_output_json",
                        report_path,
                        xml_tool_path,
                        yaml_tool_path,
                        workflow_path,
                    ]
                )

            with open(report_path) as report_fh:
                report = json.load(report_fh)

        # The Click result is the command's authoritative exit status. Galaxy's
        # raw structured report may leave its optional ``exit_code`` field null;
        # Planemo derives the command result from the report summary.
        assert result.exit_code == 0
        assert report["summary"] == {
            "num_errors": 0,
            "num_failures": 0,
            "num_skips": 0,
            "num_tests": 3,
        }
        assert construction_count == 1
        assert all(test["data"]["status"] == "success" for test in report["tests"])
        tool_jobs = [test["data"]["job"] for test in report["tests"] if test["data"].get("job")]
        assert {job["tool_id"] for job in tool_jobs} == {"cat", "embedded_echo"}
        assert all(job["state"] == "ok" for job in tool_jobs)
        # Pydantic's report model serializes optional fields as null, so select
        # by the authoritative runnable type rather than key presence.
        workflow_results = [test for test in report["tests"] if test["test_type"] == "galaxy_workflow"]
        assert len(workflow_results) == 1
        assert workflow_results[0]["data"]["invocation_details"]
        assert workflow_results[0]["data"]["invocation_details"]["details"]["invocation_state"] in {
            "scheduled",
            "completed",
        }

        from galaxy import app as galaxy_app_module

        assert galaxy_app_module.app is None
        assert not any(
            thread.name == "planemo-embedded-uvicorn" and thread.is_alive() for thread in threading.enumerate()
        )
