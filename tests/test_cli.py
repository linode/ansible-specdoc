"""Module for testing various CLI functionalities"""

# pylint: disable=protected-access

import json
import os
import unittest
from types import SimpleNamespace
from typing import Any, Dict

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
