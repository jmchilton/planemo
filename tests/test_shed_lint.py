import os
from os.path import join

from .test_utils import CliTestCase

# Injected so the reference-data fixture under tests/data/data_manager (which ships no
# .shed.yml) realizes as a shed repository for shed_lint.
DATA_MANAGER_SHED_YML = """name: "data_manager_fetch_genome_dbkeys_all_fasta"
owner: "iuc"
description: "a data manager repository"
type: "unrestricted"
categories:
  - "Data Managers"
"""


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

    def test_data_table_linting_valid(self):
        # A realistic data-manager repository (manager conf + wrapper + tool data
        # tables + loc fixtures) lints clean through the repository data-table linters.
        with self._isolate_with_test_data("data_manager/data_manager_fetch_genome_dbkeys_all_fasta") as f:
            with open(os.path.join(f, ".shed.yml"), "w") as fh:
                fh.write(DATA_MANAGER_SHED_YML)
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"])

    def test_data_table_linting_invalid(self):
        # A tool_data_table_conf referencing a loc file that is not shipped must fail
        # (MissingLocFixture), proving the galaxy-tool-util linters are wired in.
        with self._isolate_repo("bad_data_table_missing_loc"):
            self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)

    def test_data_table_linting_assembly_error(self):
        # A malformed data_manager_conf must fail *and* surface a visible diagnostic
        # (the assembly-failure message is only emitted if dispatched through lint_ctx).
        with self._isolate_repo("bad_data_manager_conf"):
            r = self._check_exit_code(["shed_lint", "--skip", "shed_remote_repository_url"], exit_code=1)
        assert "Problem assembling repository data table model" in r.output

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
