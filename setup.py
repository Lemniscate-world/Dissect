from setuptools import find_packages, setup

setup(
    name="dissect",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "tree-sitter-languages>=1.5.0"  # Modern API
    ],
    entry_points={
        "console_scripts": ["dissect=dissect.cli:main"],
    },
)
