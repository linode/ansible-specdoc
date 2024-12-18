import os
from pathlib import Path

import setuptools

current_dir = Path(__file__).parent.resolve()
readme_path = current_dir / "README.md"
requirements_path = current_dir / "requirements.txt"

def get_version():
    version_env = os.getenv("SPECDOC_VERSION")

    if version_env is not None:
        return version_env.replace("v", "")

    # Default unspecified version
    return "0.0.0"

setuptools.setup(
    name="ansible-specdoc",
    version=get_version(),
    author="Linode",
    author_email="dev-dx@linode.com",
    description="A simple tool for generating Ansible collection documentation from module spec.",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="ansible",
    url="https://github.com/linode/ansible-specdoc/",
    packages=["ansible_specdoc"],
    install_requires=requirements_path.read_text().splitlines(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": ["ansible-specdoc=ansible_specdoc.cli:main"],
    },
)
