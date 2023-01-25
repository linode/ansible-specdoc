"""
This module contains various classes to be used in Ansible modules.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


class FieldType:
    """
    Enum for Ansible-compatible field types.
    """

    list = 'list'
    dict = 'dict'
    bool = 'bool'
    integer = 'int'
    string = 'str'
    float = 'float'
    path = 'path'
    raw = 'raw'
    json_arg = 'jsonarg'
    json = 'json'
    bytes = 'bytes'
    bits = 'bits'


@dataclass
class SpecField:
    """
    A single field to be used in an Ansible module.
    """
    type: FieldType

    description: Optional[List[str]] = None
    required: bool = False
    default: Optional[Any] = None
    editable: bool = False
    conflicts_with: Optional[List[str]] = field(default_factory=lambda: [])
    no_log: bool = False
    choices: Optional[List[str]] = None
    doc_hide: bool = False
    aliases: Optional[List[str]] = None

    # These fields are only necessary for `list` and `dict` types
    element_type: Optional[FieldType] = None
    suboptions: Optional[Dict[str, 'SpecField']] = None  # Forward-declared

    # Additional fields to pass into the output Ansible spec dict
    additional_fields: Optional[Dict[str, Any]] = None

    @property
    def doc_dict(self) -> Optional[Dict[str, Any]]:
        """
        Returns the docs dict for this field.
        """

        result = self.__dict__
        if self.suboptions is not None:
            result['suboptions'] = {
                k: v.doc_dict for k, v in self.suboptions.items() if not v.doc_hide
            }

        return result


    @property
    def ansible_spec(self) -> Dict[str, Any]:
        """
        Returns the Ansible-compatible spec for this field.
        """
        result = {
            'type': str(self.type),
            'no_log': self.no_log,
            'required': self.required,
        }

        if self.default is not None:
            result['default'] = self.default

        if self.choices is not None:
            result['choices'] = self.choices

        if self.aliases is not None:
            result['aliases'] = self.aliases

        if self.suboptions is not None:
            result['options'] = {k: v.ansible_spec for k, v in self.suboptions.items()}

        if self.element_type is not None:
            result['elements'] = str(self.element_type)

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

    sample: List[str] = field(default_factory=lambda: [])
    docs_url: Optional[str] = None
    elements: Optional[FieldType] = None

@dataclass
class SpecDocMeta:
    """
    The top-level description of an Ansible module.
    """
    description: List[str]
    options: Dict[str, SpecField]

    requirements: Optional[List[str]] = None
    author: Optional[List[str]] = None
    examples: Optional[List[str]] = field(default_factory=lambda: [])
    return_values: Optional[Dict[str, SpecReturnValue]] = field(default_factory=lambda: {})

    @property
    def doc_dict(self) -> Dict[str, Any]:
        """
        Returns the documentation dict for this module.

        This isn't implemented as __dict__ because it is not 1:1 with the class layout.
        """

        result = self.__dict__

        result['options'] = {k: v.doc_dict for k, v in self.options.items() if not v.doc_hide}

        if self.return_values is not None:
            result['return_values'] = {k: v.__dict__ for k, v in self.return_values.items()}

        return result

    @property
    def ansible_spec(self) -> Dict[str, Any]:
        """
        Returns the Ansible-compatible spec for this module.
        """

        return {k: v.ansible_spec for k, v in self.options.items()}
