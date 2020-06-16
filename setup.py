import os
from setuptools import setup, find_packages

from near_api import PROJECT, VERSION


META_DATA = dict(
    name = PROJECT,
    version = VERSION,
    license = "MIT",

    author = "NEAR Inc",
    
    url = "https://github.com/near/near-api-py",

    packages = find_packages(),

    install_requires = ["requests", "base58", "ed25519"]
)

if __name__ == "__main__":
    setup(**META_DATA)

