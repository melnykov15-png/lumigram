#!/bin/bash
# Runs one workflow step script. When it fails, its error lines and last lines
# become annotations, which anyone can read on a public repository without signing in.
# Usage (as a step shell): bash mod/ci_step.sh {0}
LOG="$(mktemp)"
bash --noprofile --norc -eo pipefail "$1" 2>&1 | tee "$LOG"
STATUS="${PIPESTATUS[0]}"
if [ "$STATUS" -ne 0 ]; then
    { grep -E "(error:|ERROR:|FAILED:|fatal:|Error:|Exception|No such file)" "$LOG" | grep -v "^INFO" | head -6; tail -n 4 "$LOG"; } |
    while IFS= read -r line; do
        line="${line//'%'/'%25'}"
        echo "::error::${line:0:900}"
    done
fi
rm -f "$LOG"
exit "$STATUS"
