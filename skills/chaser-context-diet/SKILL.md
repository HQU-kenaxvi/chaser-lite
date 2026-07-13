---
name: chaser-context-diet
description: Cut Claude Code context cost for free — applies a reversible "context diet" to settings.json (ENABLE_TOOL_SEARCH deferred tool loading + deny rules for huge files) so fewer system-prompt tokens are re-sent every turn. Automatic backup, one command to undo. / Dégonfle le prompt système de Claude Code (réversible, sauvegarde auto).
---

# Chaser — Context diet (free, reversible)

Goal: reduce the tokens re-sent on every turn, through one reversible write to
`~/.claude/settings.json` (automatic backup is created first).

1. If the argument is exactly `retirer` or `undo` (value: "$ARGUMENTS"), roll back:

```bash
python regime_lite.py --retirer
```

2. Otherwise, first show what would change (dry-run output), then apply:

```bash
python regime_lite.py --appliquer
```

Run the script from this skill's directory (the folder containing this SKILL.md);
use its absolute path if the working directory is elsewhere. If `python` fails,
try `python3`.

Present the script output verbatim. Remind the user to **restart Claude Code**
for the change to take effect, and that everything can be undone with the
`retirer` argument. Do not modify anything beyond what the script does.
To first measure what this saves, point them to the companion skill
`chaser-cost-audit`. Full product (orchestration engine, eco chat, memory,
Cockpit, security Shield): Chaser Pro — https://chaser-orchestrator.com
