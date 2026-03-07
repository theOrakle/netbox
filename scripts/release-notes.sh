#!/usr/bin/env bash
set -euo pipefail

MANIFEST="custom_components/netbox/manifest.json"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOH'
Usage:
  ./scripts/release-notes.sh [tag]
EOH
  exit 0
fi

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing $MANIFEST" >&2
  exit 1
fi

TAG="${1:-$(jq -r '.version' "$MANIFEST")}"
if ! git rev-parse --verify --quiet "refs/tags/$TAG" >/dev/null; then
  echo "Tag '$TAG' does not exist locally." >&2
  echo "Usage: $0 [tag]" >&2
  exit 1
fi

PREV_TAG="$(git tag --list | sort -V | awk -v t="$TAG" '$0==t{print p; exit}{p=$0}')"
if [[ -n "$PREV_TAG" ]]; then
  RANGE="${PREV_TAG}..${TAG}"
else
  RANGE="$TAG"
fi

COMMITS="$(git log --pretty='- %s (%h)' "$RANGE" | grep -Ev '^- Release [0-9]+\.[0-9]+\.[0-9]+ ' || true)"
ROLLOUP_COMMITS="$(printf '%s\n' "$COMMITS" | grep -Ei 'rollup|dcim|ipam|org|object-changes|change log|changes last 24|changelog' || true)"
FLOW_COMMITS="$(printf '%s\n' "$COMMITS" | grep -Ei 'release|script|workflow|flow' || true)"
OTHER_COMMITS="$(printf '%s\n' "$COMMITS" | grep -Eiv 'rollup|dcim|ipam|org|object-changes|change log|changes last 24|changelog|release|script|workflow|flow' || true)"

echo "## NetBox ${TAG}"
echo
echo "### Highlights"
echo "- Added section rollup coverage for NetBox data visibility."
echo "- Added a 24-hour change-log rollup counter."
echo "- Included diagnostics and release workflow hardening updates."
echo
echo "### Rollups and Changelog"
if [[ -n "$ROLLOUP_COMMITS" ]]; then
  echo "$ROLLOUP_COMMITS"
else
  echo "- No rollup-specific commits detected in this release range."
fi
echo
echo "### Release Flow and Tooling"
if [[ -n "$FLOW_COMMITS" ]]; then
  echo "$FLOW_COMMITS"
else
  echo "- No workflow/tooling commits detected in this release range."
fi
echo
echo "### Other Changes"
if [[ -n "$OTHER_COMMITS" ]]; then
  echo "$OTHER_COMMITS"
else
  echo "- No additional changes outside rollups/tooling."
fi
echo
echo "### Notes"
echo "- Home Assistant restart recommended after update."
echo "- If using HACS, upgrade then reload/restart Home Assistant."
