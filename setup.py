import os
from setuptools import setup, find_packages


PATH = os.path.dirname(__file__)
readme = open(os.path.join(PATH, "README.md")).read()
requirements = open("requirements.txt").read().split("\n")

setup(
    url="https://github.com/st22209/Parent-Portal",
    author="FusionSid",
    version="0.1.6",
    name="kmrpp",
    description="(unofficial) cli tool to use parent portal in the terminal",
    install_requires=requirements,
    packages=find_packages(),
    long_description=readme,
    author_email="st22209@ormiston.school.nz",
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["kmr=kmrpp.__main__:main"]},
)
