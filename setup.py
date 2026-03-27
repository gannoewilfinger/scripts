from setuptools import setup, find_packages

setup(
    name='scripts',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'PyYAML',
        'paramiko',
    ],
    entry_points={
        'console_scripts': [
            'run-script=scripts.runner:main',
        ],
    },
    author='Gary Williams',
    author_email='gary@example.com',
    description='A collection of utility scripts for automation and system management.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/garywilliams/scripts',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)