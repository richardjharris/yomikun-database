from setuptools import setup, find_packages

setup(
    name='yomikun',
    version='0.9.0',
    description='Build the name database for Yomikun',
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
            'yomikun = yomikun.scripts.yomikun:main',
        ],
    },
)
