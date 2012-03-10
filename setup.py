from setuptools import setup, find_packages

long_desc = """
"""


setup(
    name='kartograph.py',
    version='0.1',
    description="",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    keywords='',
    author='Gregor Aisch',
    author_email='mail@driven-by-data.net',
    url='http://kartograph.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'test.*']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=["pyshp", "polygon", "svgfig", "pyyaml"],
    tests_require=[],
    entry_points={
        'console_scripts': [
             'kartograph = kartograph.cli:main'
        ]
    }
)
