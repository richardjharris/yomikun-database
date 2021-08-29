from setuptools import setup, find_packages

setup(
    name='yomikun',
    version='0.1',
    description='BUild the name database for Yomikun',
    author='Richard Harris',
    author_email='richardjharris@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'yourscript = yourpackage.scripts.yourscript:cli',
        ],
    },
)
