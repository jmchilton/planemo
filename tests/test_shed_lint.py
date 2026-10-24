import os
import re
import shutil
from os.path import join

import responses

from .test_utils import (
    CliTestCase,
    skip_if_environ,
    TEST_TOOLS_DIR,
)


class ShedLintTestCase(CliTestCase):
    def test_valid_repos(self):
        with self._isolate_repo("single_tool"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])
        with self._isolate_repo("multi_repos_nested"):
            self._check_exit_code(["shed_lint", "--recursive"])
        with self._isolate_repo("package_1"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])
        with self._isolate_repo("suite_1"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])
        with self._isolate_repo("workflow_1"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])

    def test_invalid_repos(self):
        # And now
        with self._isolate_repo("bad_readme_rst"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_readme_md"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=0)
        with self._isolate_repo("bad_repo_name"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_missing_include"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_missing_tool_deps"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_missing_repo_deps"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_package_category"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        with self._isolate_repo("bad_invalid_yaml"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=254)

    def test_shed_metadata_rejected_by_shed_is_an_error(self):
        # https://github.com/galaxyproject/planemo/issues/1112: the tool shed
        # rejects this name with a 400, so CI running --fail_level error -- the
        # usual way to tolerate style warnings -- must still catch it.
        with self._isolate_repo("bad_repo_name"):
            self._check_exit_code(
                ["shed_lint", "--skip", "shed_remote_repository_url", "--fail_level", "error"], exit_code=1
            )
        with self._isolate_repo("bad_unknown_category"):
            self._check_exit_code(
                ["shed_lint", "--skip", "shed_remote_repository_url", "--fail_level", "error"], exit_code=1
            )

    def test_shed_metadata_conventions_stay_warnings(self):
        # A package outside "Tool Dependency Packages" still uploads fine, so
        # it must not be promoted alongside the checks above.
        with self._isolate_repo("bad_package_category"):
            self._check_exit_code(
                ["shed_lint", "--skip", "shed_remote_repository_url", "--fail_level", "error"], exit_code=0
            )

    def test_tool_linting(self):
        # Make sure bad_invalid_tool_xml only when used with --tools.
        with self._isolate_repo("bad_invalid_tool_xml"):
            self._check_exit_code(["shed_lint"], exit_code=0)
        with self._isolate_repo("bad_invalid_tool_xml"):
            self._check_exit_code(["shed_lint", "--tools"], exit_code=1)
        with self._isolate_repo("bad_tool_no_citations"):
            self._check_exit_code(["shed_lint", "--tools"], exit_code=1)

    def test_tool_linting_required_files(self):
        # Regression test for https://github.com/galaxyproject/planemo/issues/1646:
        # a sibling file declared in <required_files> must be found in the
        # realized repository even though shed_lint copies files into a temp dir.
        with self._isolate_repo("single_tool_required_files"):
            self._check_exit_code(["shed_lint", "--tools", "--skip", "shed_remote_repository_url"])

    @responses.activate
    def test_tool_linting_doi(self):
        """--doi reaches the tool linters through shed_lint."""
        responses.add(responses.GET, "https://doi.org/10.1093/bioinformatics/bts573", status=200)
        # shed_lint's version check queries the main Tool Shed; an empty result makes it a no-op
        responses.add(responses.GET, "https://toolshed.g2.bx.psu.edu/api/repositories", json=[])
        skip_remote = ["--skip", "shed_remote_repository_url"]
        with self._isolate_repo("single_tool_required_files"):
            result = self._check_exit_code(["shed_lint", "--tools"] + skip_remote)
            assert "is a valid DOI" not in result.output
        with self._isolate_repo("single_tool_required_files"):
            result = self._check_exit_code(["shed_lint", "--tools", "--doi"] + skip_remote)
            assert "10.1093/bioinformatics/bts573 is a valid DOI" in result.output

    def test_shed_version_skips_unchanged_tools(self):
        """Same-version tools pass only when the published tool source matches."""
        with self._isolate_repo("single_tool") as f, responses.RequestsMock() as rsps:
            cat, cat2 = self._shed_version_tools(f, rsps)
            self._mock_tool_source(rsps, "cat", body=cat)
            self._mock_tool_source(rsps, "cat2", body=cat2.replace("tail-to-head", "head-to-tail"))
            result = self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
            assert "cat: unchanged since the latest installable revision (1.0+galaxy1)" in result.output
            assert "cat: version" not in result.output
            assert "cat2: version 1.0+galaxy1 is less or equal" in result.output

    def test_shed_version_errors_when_published_source_unavailable(self):
        with self._isolate_repo("single_tool") as f, responses.RequestsMock() as rsps:
            self._shed_version_tools(f, rsps)
            self._mock_tool_source(rsps, "cat", status=404)
            self._mock_tool_source(rsps, "cat2", status=404)
            result = self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
            assert "unchanged since" not in result.output
            assert "cat: version 1.0+galaxy1 is less or equal" in result.output
            assert "cat2: version 1.0+galaxy1 is less or equal" in result.output

    def _shed_version_tools(self, repo, rsps):
        """Write tools cat and cat2 at 1.0+galaxy1 and publish both at that version on the main Tool Shed."""
        cat_path = join(repo, "cat.xml")
        with open(cat_path) as fh:
            cat = fh.read().replace('version="1.0"', 'version="1.0+galaxy1"')
        cat2 = cat.replace('id="cat"', 'id="cat2"')
        with open(cat_path, "w") as fh:
            fh.write(cat)
        with open(join(repo, "cat2.xml"), "w") as fh:
            fh.write(cat2)
        api = "https://toolshed.g2.bx.psu.edu/api/repositories"
        rsps.add(responses.GET, re.compile(re.escape(api) + r"\?"), json=[{"name": "single_tool", "owner": "iuc"}])
        rsps.add(responses.GET, re.compile(re.escape(api + "/get_ordered_installable_revisions")), json=["abc123"])
        valid_tools = [{"id": "cat", "version": "1.0+galaxy1"}, {"id": "cat2", "version": "1.0+galaxy1"}]
        rsps.add(
            responses.GET,
            re.compile(re.escape(api + "/get_repository_revision_install_info")),
            json=[{}, {"valid_tools": valid_tools}, {}],
        )
        return cat, cat2

    def _mock_tool_source(self, rsps, tool_id, body="", status=200):
        url = f"https://toolshed.g2.bx.psu.edu/api/tools/iuc~single_tool~{tool_id}/versions/1.0%2Bgalaxy1/tool_source"
        rsps.add(responses.GET, url, body=body, status=status)

    @skip_if_environ("PLANEMO_SKIP_SLOW_TESTS")
    def test_tool_linting_conda_requirements(self):
        """--conda_requirements reaches the tool linters through shed_lint."""
        skip_remote = ["--skip", "shed_remote_repository_url"]
        with self._isolate_repo("single_tool_required_files") as f:
            shutil.copy(os.path.join(TEST_TOOLS_DIR, "bwa_without_requirements.xml"), f)
            result = self._check_exit_code(["shed_lint", "--tools"] + skip_remote)
            assert "Conda" not in result.output
            result = self._check_exit_code(
                ["shed_lint", "--tools", "--conda_requirements"] + skip_remote,
                exit_code=self.non_zero_exit_code,
            )
            # a usage error would also be non-zero, so pin the linter's own message
            assert "No valid package requirement tags found to check against Conda." in result.output

    def test_invalid_nested(self):
        # Created a nested repository with one good and one
        # invalid repository and make sure it runs and produces
        # a 254 (it ran to completion but one or more things failed
        # )
        with self._isolate() as f:
            for name in ["bad_invalid_yaml", "single_tool_exclude"]:
                self._copy_repo(name, join(f, name))
                self._copy_repo(name, join(f, name))
            self._check_exit_code(["shed_lint", "-r"], exit_code=254)

    def test_fail_fast(self):
        # Created a nested repository with one good and one
        # invalid repository and make sure it exits immediately with 1.
        with self._isolate() as f:
            for name in ["bad_invalid_yaml", "single_tool_exclude"]:
                self._copy_repo(name, join(f, name))
                self._copy_repo(name, join(f, name))
            r = self._check_exit_code(["shed_lint", "-r", "--fail_fast"], exit_code=1)
            assert isinstance(r.exception, RuntimeError)

    def test_ensure_metadata(self):
        with self._isolate_repo("single_tool"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])
        with self._isolate_repo("single_tool_exclude"):
            self._check_exit_code(
                ["shed_lint", "--skip", "shed_remote_repository_url", "--ensure_metadata"], exit_code=1
            )
