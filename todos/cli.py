"""
CLI of todos.

Usage
-----
todos I love batman

or

python -m todos.cli my I love batman
"""

import sys

from todos import todos


def main():
    todos.main()


if __name__ == "__main__":
    sys.exit(main())
