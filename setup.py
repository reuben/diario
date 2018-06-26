import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='diario',
    version='0.0.1',
    license='MPL-2.0',
    maintainer='Reuben Morais',
    description='Diário de classe',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ]
)
