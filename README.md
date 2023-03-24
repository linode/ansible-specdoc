# ansible-specdoc

A utility for dynamically generating documentation from an Ansible module's spec. 

This project was primarily designed for the [Linode Ansible Collection](https://github.com/linode/ansible_linode).

An example Ansible Collection using `ansible-specdoc` can be found [here](https://github.com/linode/ansible-specdoc-example).

## Usage

```sh
ansible-specdoc [-h] [-s] [-n MODULE_NAME] [-i INPUT_FILE] [-o OUTPUT_FILE] [-f {yaml,json,jinja2}] [-j] [-t TEMPLATE_FILE]

Generate Ansible Module documentation from spec.

options:
  -h, --help            show this help message and exit
  -s, --stdin           Read the module from stdin.
  -n MODULE_NAME, --module-name MODULE_NAME
                        The name of the module (required for stdin)
  -i INPUT_FILE, --input_file INPUT_FILE
                        The module to generate documentation from.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to output the documentation to.
  -f {yaml,json,jinja2}, --output_format {yaml,json,jinja2}
                        The output format of the documentation.
  -j, --inject          Inject the output documentation into the `DOCUMENTATION`, `RETURN`, and `EXAMPLES` fields of input module.
  -t TEMPLATE_FILE, --template_file TEMPLATE_FILE
                        The file to use as the template for templated formats.
  -c, --clear_injected_fields,
                        Clears the DOCUMENTATION, RETURNS, and EXAMPLES fields in specified module and sets them to an empty string.
```

---

#### Generating a templated documentation file:

```shell
ansible-specdoc -f jinja2 -t path/to/my/template.md.j2 -i path/to/my/module.py -o path/to/output/file.md
```

---

#### Dynamically generating and injecting documentation back into module constants:

```shell
ansible-specdoc -j -i path/to/my/module.py
```

NOTE: Documentation string injection requires that you have `DOCUMENTATION`, `RETURN`, and `EXAMPLES` constants defined in your module.

---

#### Generating a raw documentation string (not recommended):

```shell
ansible-specdoc -f yaml -i path/to/my/module.py
```

## Implementation

### Importing SpecDoc Classes

All of the `ansible-specdoc` classes can be imported into an Ansible module using the following statement:

```python
from ansible_specdoc.objects import *
```

Alternatively, only specific classes can be imported using the following statement:

```python
from ansible_specdoc.objects import SpecDocMeta, SpecField, SpecReturnValue, FieldType, DeprecationInfo
```

### Declaring Module Metadata
The `ansible-specdoc` specification format requires that each module exports a `SPECDOC_META` object with the following structure:

```python
SPECDOC_META = SpecDocMeta(
    description=['Module Description'],
    requirements=['python >= 3.6'],
    author=['Author Name'],
    options=module_spec,
    examples=[
        'example module usage'
    ],
    return_values={
        'my_return_value': SpecReturnValue(
            description='A generic return value.',
            type=FieldType.string,
            sample=['sample response']
        ),
    }
)
```

### Declaring Argument Specification

Each `SpecField` object translates to a parameter that can be rendered into documentation and passed into Ansible for specification.
These fields should be declared in a dict format as shown below:

```python
module_spec = {
    'example_argument': SpecField(
        type=FieldType.string,
        required=True,
        description=['An example argument.']
    )
}
```

This dict should be passed into the `options` field of the `SPECDOC_META` declaration.

### Passing Specification to Ansible

In order to retrieve the Ansible-compatible spec dict, use the `SPECDOC_META.ansible_spec` property.

### Other Notes

To prevent `ansible-specdoc` from executing module code, please ensure that all module logic executes using the following pattern:

```python
if __name__ == '__main__':
    main()
```

---

To deprecate a module, specify the `deprecated` field as follows:

```python
SPECDOC_META = SpecDocMeta(
    ...
    deprecated=DeprecationInfo(
        alternative='my.new.module',
        removed_in='1.0.0',
        why='Reason for deprecation'
    )
)
```

When deprecating a module, you will also need to update your `meta/runtime.yml` file.
Please refer to the [official Ansible deprecation documentation](https://docs.ansible.com/ansible/latest/dev_guide/module_lifecycle.html#deprecating-modules-and-plugins-in-a-collection) for more details.

## Templates

This repository provides an [example Markdown template](./template/module.md.j2) that can be used in conjunction with the `-t` argument.
