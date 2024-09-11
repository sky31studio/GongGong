from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='xtu_ems',
    version='0.0.1',
    author='LeoTan',
    author_email='leotan-studio@foxmail.com',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    requirements=requirements,
)