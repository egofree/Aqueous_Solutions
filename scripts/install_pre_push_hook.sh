#!/usr/bin/env bash
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
#
# Optional: install a local Git pre-push hook that runs scripts/check_all.sh
# before every push from this clone. The hook lives only in your clone
# (.git/hooks/pre-push); remove that file to uninstall. Skip it once with
# `git push --no-verify`.
set -eu
cd "$(dirname "$0")/.."
hook="$(git rev-parse --git-path hooks)/pre-push"
if [ -e "$hook" ] && ! grep -q "scripts/check_all.sh" "$hook"; then
  echo "A different pre-push hook already exists at $hook; not replacing it." >&2
  exit 1
fi
cat > "$hook" <<'HOOK'
#!/usr/bin/env bash
# Installed by scripts/install_pre_push_hook.sh
exec "$(git rev-parse --show-toplevel)/scripts/check_all.sh"
HOOK
chmod +x "$hook"
echo "Installed $hook"
