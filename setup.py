from setuptools import setup, find_packages

setup(
    name="retry_utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Gary Williams",
    author_email="gary@example.com",
    description="A Python library for retry logic with exponential backoff",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/garywilliams/retry_utils",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)