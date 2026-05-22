"""Nox sessions — uv-backed.

Each session shells out to ``uv run`` (uv owns the environment + lockfile),
so there is no nox-managed virtualenv and no nox-poetry. Run e.g.
``nox -s tests`` or just use ``uv run pytest`` directly.
"""

import nox

PACKAGE = "gwbase"
PYTHON_VERSIONS = ["3.12"]

nox.options.default_venv_backend = "none"
nox.options.sessions = ("lint", "mypy", "tests", "xdoctest")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.run("uv", "run", "--all-groups", "pytest", *session.posargs, external=True)


@nox.session(python=PYTHON_VERSIONS)
def mypy(session: nox.Session) -> None:
    """Type-check the package."""
    session.run(
        "uv", "run", "--all-groups", "mypy", "src", *session.posargs, external=True
    )


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Lint + format-check with ruff."""
    session.run("uv", "run", "ruff", "check", ".", external=True)
    session.run("uv", "run", "ruff", "format", "--check", ".", external=True)


@nox.session(python=PYTHON_VERSIONS)
def xdoctest(session: nox.Session) -> None:
    """Run examples embedded in docstrings."""
    session.run(
        "uv",
        "run",
        "--all-groups",
        "python",
        "-m",
        "xdoctest",
        PACKAGE,
        *session.posargs,
        external=True,
    )


@nox.session(name="docs-build", python=PYTHON_VERSIONS)
def docs_build(session: nox.Session) -> None:
    """Build the Sphinx docs."""
    session.run(
        "uv",
        "run",
        "--all-groups",
        "sphinx-build",
        "docs",
        "docs/_build",
        external=True,
    )
