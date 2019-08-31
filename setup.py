from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="astroAPIServer",
    description="",
    version="0.0.1a1",
    url="http://github.com/ketozhang/astroAPIServer",
    author="Keto Zhang",
    author_email="keto.zhang@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['astroapiserver'],
    python_requires='>=3.3',
    install_requires=[
        "flask-wtf>=0.14.2",
        "flask>=1.1.1",
        "pyjwt>=1.7.1",
        "pyyaml>=5.1.2",
    ]
)
