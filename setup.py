from setuptools import setup

setup(
    name="pngstuff",
    version="0.1.0",
    py_modules=["pngstuff"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "pngstuff = pngstuff:cli",
        ],
    },
)
