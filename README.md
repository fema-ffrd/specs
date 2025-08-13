# specs

FEMA FFRD Specifications. IN PROGRESS.

https://fema-ffrd.github.io/specs/

## Setup

1. Create a Python virtual environment.

```
$ python -m venv venv-specs
$ source ./venv-specs/bin/activate
(venv-specs) $
```

2. Install project dependencies.

```
(venv-specs) $ pip install .
```

3. Run the local `mkdocs` server.

```
(venv-specs) $ mkdocs serve
```

### Optional Setup - Markdown Formatting Pre-Commit Hook

To set up a pre-commit hook for [mdformat](https://mdformat.readthedocs.io/en/stable/index.html) to automatically format Markdown files within the repository:

```
(venv-specs) $ pre-commit install
```
