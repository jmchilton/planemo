"""Opt-in integration coverage for package-installed embedded Galaxy.

Run with ``PLANEMO_TEST_EMBEDDED_GALAXY=1`` in an environment containing a
Galaxy build with galaxyproject/galaxy#23360.
"""

import json
import os
import threading

from .test_utils import (
    CliTestCase,
    skip_unless_environ,
    TEST_TOOLS_DIR,
)


class EmbeddedGalaxyIntegrationTestCase(CliTestCase):
    @skip_unless_environ("PLANEMO_TEST_EMBEDDED_GALAXY")
    def test_yaml_tool_runs_through_embedded_worker(self):
        tool_path = os.path.join(TEST_TOOLS_DIR, "embedded_echo.yml")

        with self._isolate() as test_directory:
            report_path = os.path.join(test_directory, "embedded-report.json")
            result = self._check_exit_code(
                [
                    "test",
                    "--engine",
                    "embedded_galaxy",
                    "--no_dependency_resolution",
                    "--test_output_json",
                    report_path,
                    tool_path,
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
            "num_tests": 1,
        }
        test_data = report["tests"][0]["data"]
        assert test_data["status"] == "success"
        assert test_data["job"]["state"] == "ok"
        assert test_data["job"]["tool_id"] == "embedded_echo"

        from galaxy import app as galaxy_app_module

        assert galaxy_app_module.app is None
        assert not any(
            thread.name == "planemo-embedded-uvicorn" and thread.is_alive() for thread in threading.enumerate()
        )
