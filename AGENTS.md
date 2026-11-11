# Agent Guidelines

## Project References

- Use [README.md](README.md) for CLI usage, spec declarations, and templates, and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and vulnerability-reporting guidance.
- Follow [pyproject.toml](pyproject.toml) for dependency, supported-Python, and formatter configuration, and [Makefile](Makefile) for development commands.

## Code Boundaries

- Keep module loading, rendering, and CLI orchestration in [ansible_specdoc/cli.py](ansible_specdoc/cli.py); metadata dataclasses and Ansible spec/document conversions belong in [ansible_specdoc/objects.py](ansible_specdoc/objects.py).
- Use [template/module.md.j2](template/module.md.j2) as the reference for Jinja2 output and [tests/test_modules/module_1.py](tests/test_modules/module_1.py) as the existing trusted module fixture.

## Development Checks

- Run commands from the repository root. Use `make deps` to install the editable package and development dependencies; see [setup and building](README.md#building) for packaging details.
- For CLI changes, run `pytest -q tests/test_cli.py`. Before completing Python changes, run `make test` and `make lint`.
- Extend the existing `unittest` and mock-based tests in [tests/test_cli.py](tests/test_cli.py) rather than introducing a separate test framework or duplicating fixtures.
- Do not use `make build` merely as a validation command: it rewrites [ansible_specdoc/version.py](ansible_specdoc/version.py). Follow the documented release-version flow when packaging is requested.

## Behavioral Constraints

- Module inputs execute Python code. Do not run untrusted inputs or bypass the CLI acknowledgement with `--yes` merely to make automation succeed; follow the [security warning](README.md#security-warning).
- In `CLI._inject_docs`, replace only the values of module-level `DOCUMENTATION`, `RETURN`, and `EXAMPLES` assignments. Nested assignments, attribute assignments, and annotations without values must not satisfy missing-field checks.
- When changing `CLI._inject_docs`, preserve surrounding source, comments, whitespace, UTF-8 byte offsets, CRLF input, and idempotence. Extend `test_docs_injection_preserves_source` and `test_docs_injection_missing_fields`; use `pytest -q tests/test_cli.py -k 'docs_injection or docs_file'` for focused validation.

## Delivery

- Use [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) for pull requests and [.github/workflows/ci.yml](.github/workflows/ci.yml) as the source of required CI checks.