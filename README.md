# ansible-specdoc

A utility for dynamically generating documentation from an Ansible module's spec. This is primarily designed for the [Linode Ansible Collection](https://github.com/linode/ansible_linode).

## Usage

```sh
ansible-specdoc [-h] [-s] [-n MODULE_NAME] [-i INPUT_FILE] [-o OUTPUT_FILE] [-f {yaml,json,jinja2}] [-j] [-t TEMPLATE_FILE]

Generate Ansible Module documentation from spec.

optional arguments:
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
  -j, --inject          Inject the output documentation into the `DOCUMENTATION` field of input module.
  -t TEMPLATE_FILE, --template_file TEMPLATE_FILE
                        The file to use as the template for templated formats.
```

## Specification Format

### Module Metadata
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

### Argument Specification

Certain fields may automatically be passed into the Ansible-compatible spec dict.

Spec fields may additional metadata that will appear in the documentation.

For example:

```python
module_spec = {
    'example_argument': SpecField(
        type=FieldType.string,
        required=True,
        description=['An example argument.']
    )
}
```

In order to retrieve the Ansible-compatible spec dict, use the `SPECDOC_META.ansible_spec` property.
