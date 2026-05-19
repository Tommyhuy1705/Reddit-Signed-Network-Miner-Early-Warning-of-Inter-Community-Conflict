"""helpers.py
Common helper functions for the project.
"""


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
