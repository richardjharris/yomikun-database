from setuptools import setup, find_packages

setup(
    name='yomikun',
    version='0.1',
    description='Build the name database for Yomikun',
    author='Richard Harris',
    author_email='richardjharris@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['yomikun'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'yomikun = yomikun.scripts.yomikun:main',
        ],
    },
)
