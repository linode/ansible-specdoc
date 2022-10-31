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

The `ansible-specdoc` specification format requires that each module exports a `specdoc_meta` dict with the following structure:

```python
specdoc_meta = dict(
    description=['Module Description'],
    requirements=['python >= 3.6'],
    author=['Author Name'],
    spec=module_spec,
    examples=[
        'example module usage'
    ],
    return_values=dict(
        my_return_value=dict(
            description='A generic return value.',
            type='str',
            sample=['sample response']
        ),
    )
)
```

The `spec` field of the `specdoc_meta` struct should refer to an
[Ansible argument specification](https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html#argument-spec).

Spec fields may contain an additional `description` field that will appear in the documentation.

For example:

```python
module_spec = dict(
    example_argument=dict(type='str', required=True, description='An example argument.')
)
```
