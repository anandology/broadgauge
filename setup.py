from setuptools import setup, find_packages

setup(
    name='broadgauge',
    version="0.1.0",
    license="BSD",
    install_requries=[
        'web.py',
        'Jinja2',
    ],
    packages=find_packages(),
    author='Anand Chitipothu',
    author_email="anandology@gmail.com",
    platforms='any',
)