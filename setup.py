import sys

from setuptools import find_packages, setup


with open("README.md") as f:
    readme = f.read()

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setup_requirements = [] + pytest_runner
test_requirements = ["pytest", "parameterized", "mongomock"]

install_requires = [
    "Click",
    "yagooglesearch @ git+ssh://git@github.com/pguridi/yagooglesearch.git#egg=some-pkg",
    "playwright",
    "playwright-stealth",
    "tqdm"
]

setup(
    name="linkedin_scraper",
    version="0.1.1",
    description="LinkedIn scraper PoC",
    long_description=readme,
    author="Pedro Guridi",
    author_email="pedro.guridi@gmail.com",
    install_requires=install_requires,
    test_suite="tests",
    tests_require=test_requirements,
    url="",
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': [
            'linkedin_scraper = linkedin_scraper.cli:scrape_companies_csv',
        ],
    },
    include_package_data=False,
    packages=find_packages(exclude=["tests"]),
)
