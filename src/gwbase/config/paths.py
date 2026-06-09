"""XDG Base Directory convention for gwbase services.

A small inline helper (NOT a shared package — gwproactor keeps its own
``Paths`` class). Default file locations live under per-service XDG
directories instead of system-level ``/etc/gridworks/...``:

  - config: ``~/.config/gridworks/<service_name>/``
  - data:   ``~/.local/share/gridworks/<service_name>/``
  - state:  ``~/.local/state/gridworks/<service_name>/`` (incl. logs)

Spec: ``wiki/gridworks-base/designs/support-non-gnode-actors/xdg-paths.md``.
"""

from pathlib import Path

import xdg

BASE = "gridworks"


def config_dir(service_name: str) -> Path:
    """e.g. ~/.config/gridworks/<service_name>/"""
    return xdg.xdg_config_home() / BASE / service_name


def data_dir(service_name: str) -> Path:
    """e.g. ~/.local/share/gridworks/<service_name>/"""
    return xdg.xdg_data_home() / BASE / service_name


def state_dir(service_name: str) -> Path:
    """e.g. ~/.local/state/gridworks/<service_name>/"""
    return xdg.xdg_state_home() / BASE / service_name


def log_dir(service_name: str) -> Path:
    """e.g. ~/.local/state/gridworks/<service_name>/log/"""
    return state_dir(service_name) / "log"


def g_node_gt_path(service_name: str) -> Path:
    """e.g. ~/.config/gridworks/<service_name>/g.node.gt.json"""
    return config_dir(service_name) / "g.node.gt.json"


def mkdirs(service_name: str) -> None:
    """Create config/data/state/log dirs for this service if absent.
    Safe to call repeatedly."""
    for d in (
        config_dir(service_name),
        data_dir(service_name),
        state_dir(service_name),
        log_dir(service_name),
    ):
        d.mkdir(parents=True, exist_ok=True)
