from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in erpnext_reportlab/__init__.py
from erpnext_reportlab import __version__ as version

setup(
    name="erpnext_reportlab",
    version=version,
    description="Advanced PDF generation using ReportLab for ERPNext",
    author="ERPNext Team",
    author_email="developers@erpnext.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)