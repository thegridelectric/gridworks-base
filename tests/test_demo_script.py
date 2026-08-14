"""The demo script is importable.

`hello_rabbit.py` sits at the repo root and nothing imports it, so a moved
or deleted symbol in its import block otherwise survives a green suite (as
the `gwbase.sema.wrapped` removal proved). Executing the module runs its
imports only — the demo body is behind ``__main__``.
"""

import importlib.util
from pathlib import Path


def test_demo_script_imports() -> None:
    path = Path(__file__).parent.parent / "hello_rabbit.py"
    spec = importlib.util.spec_from_file_location("hello_rabbit", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    assert callable(module.demo)
