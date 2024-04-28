from setuptools import setup

requires = [
    "lxml",
]

python_requires = ">=3.10"

version = "2.1"
setup(
    name="kbinxml",
    description="Decoder/encoder for Konami's binary XML format",
    long_description="See Github for up to date documentation",
    version=version,
    entry_points={
        "console_scripts": ["kbinxml=kbinxml:main"],
    },
    packages=["kbinxml"],
    url="https://github.com/mon/kbinxml/",
    download_url="https://github.com/mon/kbinxml/archive/{}.tar.gz".format(version),
    author="mon",
    author_email="me@mon.im",
    install_requires=requires,
)
