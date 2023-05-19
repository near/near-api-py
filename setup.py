from setuptools import setup, find_packages

META_DATA = dict(
    name="near-api",
    version="0.2.1",
    license="MIT",

    author="NEAR Inc",

    url="https://github.com/near/near-api-py",

    packages=find_packages(),

    install_requires=["requests", "base58", "pynacl"]
)

if __name__ == "__main__":
    setup(**META_DATA)
