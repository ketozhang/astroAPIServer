from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="astroAPIServer",
    description="",
    version="2020.1b2",
    url="http://github.com/ketozhang/astroAPIServer",
    author="Keto Zhang",
    author_email="keto.zhang@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["astroapiserver"],
    python_requires=">=3.3",
    install_requires=[
        "astropy>=4.0",
        "flask>=1.1",
        "flask-wtf>=0.14",
        "pandas>=0.25",
        "pyjwt>=1.7",
        "pyyaml>=5.1",
        "webargs>5.5",
    ],
)
