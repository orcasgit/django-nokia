from setuptools import setup, find_packages

required = [line for line in open('requirements/base.txt').read().split("\n")]

setup(
    name="django-nokia",
    version=__import__("nokiaapp").__version__,
    author="orcas",
    author_email="bpitcher@orcasinc.com",
    packages=find_packages(),
    install_requires=["setuptools"] + required,
    include_package_data=True,
    url="https://github.com/orcasgit/django-nokia/",
    license="License :: OSI Approved :: Apache Software License",
    description="Django integration for python-nokia",
    long_description=open("README.md").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: Apache Software License',
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    test_suite="runtests.runtests"
)
