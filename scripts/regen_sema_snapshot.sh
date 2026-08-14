#!/usr/bin/env bash
#
# Regenerates the repo's vendored Sema snapshot from the canonical sema
# repo. The vendored tree is GENERATED — never hand-edit it; edit the seed
# (or the sema definitions) and re-run.
#
# The build mechanics are the sema CLI's (`sema snapshot --help` is the
# source of truth). The CLI refuses to run from a dirty sema checkout and
# writes only under <sema>/output, so the snapshot is reproducible from
# the sema commit the checkout sits on — check out the ref you intend to
# ship from before running.
#
# Usage:
#   scripts/regen_sema_snapshot.sh                 # sibling ../sema checkout
#   SEMA_REPO=/path/to/sema scripts/regen_sema_snapshot.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEMA_REPO="${SEMA_REPO:-$(cd "${REPO_ROOT}/../sema" 2>/dev/null && pwd || true)}"

PACKAGE_NAME="gwbase"
SEED="${REPO_ROOT}/src/gwbase/sema_seed_request.yaml"
VENDOR_DIR="${REPO_ROOT}/src/gwbase/sema"


if [[ -z "${SEMA_REPO}" || ! -d "${SEMA_REPO}" ]]; then
  echo "error: sema repo not found." >&2
  echo "       set SEMA_REPO=/path/to/sema and re-run (default looked for a" >&2
  echo "       sibling checkout at ${REPO_ROOT}/../sema)." >&2
  exit 1
fi

echo "==> sema repo: ${SEMA_REPO} @ $(git -C "${SEMA_REPO}" rev-parse --short HEAD)"
echo "==> seed:      ${SEED}"
echo "==> package:   ${PACKAGE_NAME}"

cd "${SEMA_REPO}"
echo "==> sema snapshot prepare"
# --allow-staged: the seed includes fis.connect.claims, which is deliberately
# a staging word while the broker auth gate it serves is still being built.
# Staging words are mutable in place, so this snapshot is dev-only until that
# word is promoted to published — at which point drop this flag, and let the
# CLI's default guard keep the next staging word out by accident.
uv run sema snapshot prepare --allow-staged "${SEED}"
echo "==> sema snapshot build --package-name ${PACKAGE_NAME}"
uv run sema snapshot build --package-name "${PACKAGE_NAME}"

echo "==> mirror ${SEMA_REPO}/output/sema -> ${VENDOR_DIR}"
rsync -a --delete --exclude='__pycache__' \
  "${SEMA_REPO}/output/sema/" "${VENDOR_DIR}/"

echo "==> rebrand the codec boundary classes GwBase*"
# gwbase is a LIBRARY: the applications built on it each vendor their own
# snapshot, whose generated runtime uses the same generic class names
# (SemaCodec, SemaType, SemaError). If gwbase also exported those names, an
# application would hold two codecs both called SemaCodec — its own
# vocabulary's and the transport layer's — and the layer an import belongs
# to would vanish from the code. So gwbase's copies carry the GwBase prefix,
# applied here on every regen rather than by hand, and the generic names do
# not exist in this repo at all.
python3 - "$VENDOR_DIR" <<'PY'
import pathlib
import re
import sys

RENAMES = {
    "SemaCodec": "GwBaseSemaCodec",
    "SemaType": "GwBaseSemaType",
    "SemaError": "GwBaseSemaError",
}
vendor = pathlib.Path(sys.argv[1])
for f in vendor.rglob("*.py"):
    text = f.read_text()
    for old, new in RENAMES.items():
        # word-boundary on both sides: leaves DegradedSemaType and the
        # already-prefixed names alone
        text = re.sub(rf"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])", new, text)
    f.write_text(text)

leaks = [
    str(f)
    for f in vendor.rglob("*.py")
    for old in RENAMES
    if re.search(rf"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])", f.read_text())
]
if leaks:
    sys.exit(f"rebrand incomplete — generic names remain in: {leaks}")
print("rebranded: " + ", ".join(f"{o} -> {n}" for o, n in RENAMES.items()))
PY

echo "==> done. review the diff (git status) and run your repo's tests."
