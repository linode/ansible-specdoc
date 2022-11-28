import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

def get_long_description():
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()

    return long_description

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
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="ansible",
    url="https://github.com/linode/ansible-specdoc/",
    packages=['ansible_specdoc'],
    install_requires=[
        'PyYAML==5.4.1',
        'Jinja2==3.0.1',
        'redbaron==0.9.2'
    ],
    setup_requires=['setupext_janitor'],
    python_requires='>=3',
    entry_points={
        'console_scripts': ['ansible-specdoc=ansible_specdoc.cli:main'],
        'distutils.commands': ['clean = setupext_janitor.janitor:CleanCommand']
    }
)
