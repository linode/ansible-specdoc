"""
This module contains various classes to be used in Ansible modules.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml


class FieldType:
    """
    Enum for Ansible-compatible field types.
    """

    list = "list"
    dict = "dict"
    bool = "bool"
    integer = "int"
    string = "str"
    float = "float"
    path = "path"
    raw = "raw"
    json_arg = "jsonarg"
    json = "json"
    bytes = "bytes"
    bits = "bits"


@dataclass
class DeprecationInfo:
    """
    Contains info about a deprecated module.
    """

    alternative: str

    removed_in: Optional[str] = None  # Mutually exclusive with removed_by_date
    removed_by_date: Optional[str] = None

    why: Optional[str] = None

    @property
    def ansible_doc_dict(self):
        """
        Returns a dict representing this deprecation.
        """

        if self.removed_in and self.removed_by_date:
            raise ValueError(
                "removed_in and removed_by_date are conflicting fields"
            )

        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class SpecField:
    """
    A single field to be used in an Ansible module.
    """

    type: FieldType

    description: Union[str, List[str]] = ""
    version_added: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    editable: bool = False
    conflicts_with: Optional[List[str]] = field(default_factory=lambda: [])
    no_log: bool = False
    choices: Optional[List[Any]] = None
    doc_hide: bool = False
    aliases: Optional[List[str]] = None

    # These fields are only necessary for `list` and `dict` types
    element_type: Optional[FieldType] = None
    suboptions: Optional[Dict[str, SpecField]] = None  # Forward-declared

    # Additional fields to pass into the output Ansible spec dict
    additional_fields: Optional[Dict[str, Any]] = None

    @property
    def ansible_doc_dict(self) -> Optional[Dict[str, Any]]:
        """
        Returns the Ansible-compatible docs dict for this field.
        """

        if isinstance(self.description, str):
            self.description = [self.description]

        result = {
            "type": self.type,
            "required": self.required,
            "description": self.description,
        }

        if self.default is not None:
            result["default"] = self.default

        if self.choices is not None:
            result["choices"] = self.choices

        if self.element_type is not None:
            result["elements"] = self.element_type

        if self.aliases is not None:
            result["aliases"] = self.aliases

        if self.version_added is not None:
            result["version_added"] = self.version_added

        if self.suboptions is not None:
            result["suboptions"] = {
                k: v.ansible_doc_dict for k, v in self.suboptions.items()
            }

        return result

    @property
    def doc_dict(self) -> Optional[Dict[str, Any]]:
        """
        Returns the docs dict for this field.
        """

        result = copy.deepcopy(self.__dict__)

        if isinstance(result["description"], str):
            result["description"] = [result["description"]]

        if self.suboptions is not None:
            result["suboptions"] = {
                k: v.doc_dict
                for k, v in self.suboptions.items()
                if not v.doc_hide
            }

        return result

    @property
    def ansible_spec(self) -> Dict[str, Any]:
        """
        Returns the Ansible-compatible spec for this field.
        """
        result = {
            "type": str(self.type),
            "no_log": self.no_log,
            "required": self.required,
        }

        if self.default is not None:
            result["default"] = self.default

        if self.choices is not None:
            result["choices"] = self.choices

        if self.aliases is not None:
            result["aliases"] = self.aliases

        if self.suboptions is not None:
            result["options"] = {
                k: v.ansible_spec for k, v in self.suboptions.items()
            }

        if self.element_type is not None:
            result["elements"] = str(self.element_type)

        if self.additional_fields is not None:
            result = {**result, **self.additional_fields}

        return result


@dataclass
class SpecReturnValue:
    """
    A description of an Ansible module's return value.
    """

    description: str
    type: FieldType

    returned: str = "always"
    version_added: Optional[str] = None
    sample: List[str] = field(default_factory=lambda: [])
    contains: Optional[Dict[str, SpecReturnValue]] = None
    docs_url: Optional[str] = None
    elements: Optional[FieldType] = None

    @property
    def doc_dict(self) -> Dict[str, Any]:
        """
        Returns a documentation dict for a return value.
        """
        result = self.__dict__

        if self.contains is not None:
            result["contains"] = {
                k: v.doc_dict for k, v in self.contains.items()
            }

        return result

    @property
    def ansible_doc(self) -> Dict[str, Any]:
        """
        Returns an Ansible-compatible documentation dict for a return value.
        """
        result = {
            "description": self.description,
            "type": str(self.type),
            "returned": self.returned,
            "sample": json.loads("".join(self.sample)),
        }

        if self.elements is not None:
            result["elements"] = self.elements

        if self.contains is not None:
            result["contains"] = {
                k: v.ansible_doc for k, v in self.contains.items()
            }

        if self.version_added is not None:
            result["version_added"] = self.version_added

        return result


@dataclass
class SpecDocMeta:
    """
    The top-level description of an Ansible module.
    """

    description: Union[str, List[str]]
    options: Dict[str, SpecField]

    deprecated: Optional[DeprecationInfo] = None
    version_added: Optional[str] = None
    short_description: Optional[str] = None
    requirements: Optional[List[str]] = None
    author: Optional[List[str]] = None
    examples: Optional[List[str]] = field(default_factory=lambda: [])
    return_values: Optional[Dict[str, SpecReturnValue]] = field(
        default_factory=lambda: {}
    )
    notes: Optional[List[str]] = field(default_factory=lambda: [])

    @property
    def doc_dict(self) -> Dict[str, Any]:
        """
        Returns the documentation dict for this module.

        This isn't implemented as __dict__ because it is not 1:1 with the class layout.
        """

        result = self.__dict__

        if isinstance(result["description"], str):
            result["description"] = [result["description"]]

        result["options"] = {
            k: v.doc_dict for k, v in self.options.items() if not v.doc_hide
        }

        if self.return_values is not None:
            result["return_values"] = {
                k: v.doc_dict for k, v in self.return_values.items()
            }

        if self.deprecated is not None:
            result["deprecated"] = self.deprecated.ansible_doc_dict

        return result

    @property
    def ansible_doc(self) -> Tuple[Dict[str, Any], Dict[str, Any], List]:
        """
        Returns the Ansible-compatible documentation dicts for this module.
        """

        description = (
            self.description
            if isinstance(self.description, str)
            else self.description
        )

        documentation = {
            "description": description,
            "short_description": (
                self.short_description
                if self.short_description is not None
                else " ".join(description)
            ),
            "author": self.author,
            "requirements": self.requirements,
            "notes": self.notes,
            "options": {
                k: v.ansible_doc_dict
                for k, v in self.options.items()
                if not v.doc_hide
            },
        }

        if self.version_added is not None:
            documentation["version_added"] = self.version_added

        if self.deprecated is not None:
            documentation["deprecated"] = self.deprecated.ansible_doc_dict

        return_values = {
            k: v.ansible_doc for k, v in self.return_values.items()
        }

        examples = yaml.safe_load("\n".join(self.examples))

        return documentation, return_values, examples

    @property
    def ansible_spec(self) -> Dict[str, Any]:
        """
        Returns the Ansible-compatible spec for this module.
        """

        return {k: v.ansible_spec for k, v in self.options.items()}
