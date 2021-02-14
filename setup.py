from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

version = {}
with open("todos/version.py") as f:
    exec(f.read(), version)

setup(
    name="todos",
    version=version["__version__"],
    description="A small todos app.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/e-k-m/todos",
    author="Eric Matti",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="todos",
    packages=find_packages(include=["todos", "todos.*"]),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[],
    entry_points={"console_scripts": ["todos=todos.cli:main"]},
)
