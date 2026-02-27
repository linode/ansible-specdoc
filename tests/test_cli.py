"""Module for testing various CLI functionalities"""

# pylint: disable=protected-access

import io
import json
import os
import unittest
from types import SimpleNamespace
from typing import Any, Dict
from unittest import mock

import yaml

from ansible_specdoc.cli import CLI, SpecDocModule
from ansible_specdoc.objects import SpecDocMeta, SpecField
from tests.test_modules import module_1

TEST_MODULES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "test_modules"
)
TEST_FILES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "test_files"
)

MODULE_1_DIR = os.path.join(TEST_MODULES_DIR, "module_1.py")


class TestDocs(unittest.TestCase):
    """Docs generation tests"""

    @staticmethod
    def assert_docs_dict_valid(
        original_spec: SpecDocMeta, generated_spec: Dict[str, Any]
    ):
        """Assert that the two specs are matching"""

        assert generated_spec.get("description") == original_spec.description
        assert generated_spec.get("requirements") == original_spec.requirements
        assert generated_spec.get("author") == original_spec.author
        assert generated_spec.get("examples") == original_spec.examples
        assert (
            generated_spec.get("deprecated")
            == original_spec.deprecated.ansible_doc_dict
        )
        assert generated_spec.get("return_values") == {
            k: v.__dict__ for k, v in original_spec.return_values.items()
        }

        def assert_spec_recursive(
            yaml_spec: Dict[str, Any], module_spec: Dict[str, SpecField]
        ):
            """Recursively assert that spec options match"""

            for key, value in yaml_spec.items():
                # If item is rendered regardless of doc_hide
                if module_spec.get(key).doc_hide:
                    raise Exception("item not hidden for doc_hide value")

                assert value.get("type") == module_spec.get(key).type
                assert value.get("required") == module_spec.get(key).required
                assert (
                    value.get("description") == module_spec.get(key).description
                )

                options = value.get("suboptions")
                if options is not None:
                    assert_spec_recursive(
                        options, module_spec.get(key).suboptions
                    )

                editable = value.get("editable")
                if editable:
                    assert editable == module_spec.get(key).editable

                conflicts_with = value.get("conflicts_with")
                if conflicts_with:
                    assert conflicts_with == module_spec.get(key).conflicts_with

        assert_spec_recursive(
            generated_spec.get("options"), original_spec.options
        )

    @staticmethod
    def test_docs_yaml_module_override():
        """Test that module names can be overridden"""
        module = SpecDocModule()

        module.load_file(MODULE_1_DIR, "really_cool_mod")

        assert (
            yaml.safe_load(module.generate_yaml()).get("module")
            == "really_cool_mod"
        )

    def test_docs_file_yaml(self):
        """Test that the YAML output is valid"""
        module = SpecDocModule()

        module.load_file(MODULE_1_DIR)

        output_yaml = yaml.safe_load(module.generate_yaml())

        assert output_yaml.get("module") == "module_1"

        self.assert_docs_dict_valid(module_1.SPECDOC_META, output_yaml)

    def test_docs_file_json(self):
        """Test that the JSON output is valid"""
        module = SpecDocModule()

        module.load_file(MODULE_1_DIR)

        output_json = json.loads(module.generate_json())

        assert output_json.get("module") == "module_1"

        self.assert_docs_dict_valid(module_1.SPECDOC_META, output_json)

    def test_docs_file_ansible(self):
        """Test that the JSON output is valid"""
        module = SpecDocModule()

        module.load_file(MODULE_1_DIR)

        output_json = json.loads(module.generate_json())

        assert output_json.get("module") == "module_1"

        self.assert_docs_dict_valid(module_1.SPECDOC_META, output_json)

    @staticmethod
    def test_docs_file_template():
        """Test that Jinja2 outputs are valid"""
        module = SpecDocModule()

        module.load_file(MODULE_1_DIR)

        with open(os.path.join(TEST_FILES_DIR, "template.j2"), "r") as file:
            template_str = file.read()

        output = module.generate_jinja2(template_str)

        assert "really cool module name: module_1" in output

    @staticmethod
    def test_docs_file_injection():
        """Test that documentation fields are injected correctly"""
        module_path = MODULE_1_DIR

        module = SpecDocModule()

        module.load_file(module_path)

        docs, returns, examples = module.generate_ansible_doc_yaml()

        with open(MODULE_1_DIR, "r") as file:
            module_contents = file.read()

        cli = CLI()
        cli._mod = module

        output = cli._inject_docs(module_contents)

        assert f'DOCUMENTATION = r"""\n{docs}"""' in output
        assert f'EXAMPLES = r"""\n{examples}"""' in output
        assert f'RETURN = r"""\n{returns}"""' in output
        assert "{" not in returns

    @staticmethod
    def test_docs_file_clear():
        """Test that documentation fields are injected correctly"""
        module_path = MODULE_1_DIR

        module = SpecDocModule()

        module.load_file(module_path)

        with open(MODULE_1_DIR, "r") as file:
            module_contents = file.read()

        cli = CLI()
        cli._mod = module

        cli._args = SimpleNamespace(clear_injected_fields=True)

        output = cli._inject_docs(module_contents)

        assert 'DOCUMENTATION = r"""\n"""' in output
        assert 'EXAMPLES = r"""\n"""' in output
        assert 'RETURN = r"""\n"""' in output


class TestCLIPrompt(unittest.TestCase):
    """Tests for CLI confirmation prompt and non-interactive behaviors."""

    def setUp(self):
        """Set up test module path for CLI prompt tests."""
        self.module_path = MODULE_1_DIR

    def run_cli_with_args(self, args, input_value=None, isatty=True):
        """Run CLI with given args, simulating input and TTY,
        and capture stderr and exit behavior."""
        # Patch sys.stdin, sys.stderr, sys.exit, and input as needed
        with (
            mock.patch("sys.argv", ["prog"] + args),
            mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
            mock.patch("sys.exit") as mock_exit,
        ):
            if input_value is not None:
                with (
                    mock.patch("builtins.input", return_value=input_value),
                    mock.patch("sys.stdin.isatty", return_value=isatty),
                ):
                    cli = CLI()
                    cli.execute()
            else:
                with mock.patch("sys.stdin.isatty", return_value=isatty):
                    cli = CLI()
                    cli.execute()
            return mock_stderr.getvalue(), mock_exit

    def test_prompt_yes_proceeds(self):
        """Prompt accepts 'yes' and proceeds without exit."""
        stderr, mock_exit = self.run_cli_with_args(
            ["-i", self.module_path, "-f", "json"],
            input_value="yes",
            isatty=True,
        )
        self.assertIn(
            "WARNING: You are about to import and execute code", stderr
        )
        mock_exit.assert_not_called()

    def test_prompt_no_aborts(self):
        """Prompt rejects non-'yes' and exits with code 1."""
        stderr, mock_exit = self.run_cli_with_args(
            ["-i", self.module_path, "-f", "json"],
            input_value="no",
            isatty=True,
        )
        self.assertIn("Aborted.", stderr)
        mock_exit.assert_called_once_with(1)

    def test_prompt_eof_aborts(self):
        """Prompt receives EOF and exits with code 1."""
        with (
            mock.patch(
                "sys.argv", ["prog", "-i", self.module_path, "-f", "json"]
            ),
            mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
            mock.patch("sys.stdin.isatty", return_value=True),
            mock.patch("builtins.input", side_effect=EOFError),
            mock.patch("sys.exit") as mock_exit,
        ):
            cli = CLI()
            cli.execute()
            self.assertIn("Aborted: No input received.", mock_stderr.getvalue())
            mock_exit.assert_called_once_with(1)

    def test_noninteractive_without_yes_fails(self):
        """Non-interactive run without --yes fails with error and exit code 1."""
        stderr, mock_exit = self.run_cli_with_args(
            ["-i", self.module_path, "-f", "json"], isatty=False
        )
        self.assertIn("ERROR: Interactive confirmation required", stderr)
        mock_exit.assert_called_once_with(1)

    def test_noninteractive_with_yes_succeeds(self):
        """Non-interactive run with --yes proceeds without exit."""
        stderr, mock_exit = self.run_cli_with_args(
            ["-i", self.module_path, "-f", "json", "--yes"], isatty=False
        )
        self.assertIn(
            "WARNING: You are about to import and execute code", stderr
        )
        mock_exit.assert_not_called()
