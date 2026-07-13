# Chaser Lite — cut the hidden cost of Claude Code

Free tools from **Chaser** (https://chaser-orchestrator.com) that measure and
shrink the token cost of your Claude Code setup. 100% local, read-only audit,
reversible changes, zero dependencies (Python stdlib only).

- **chaser-cost-audit** — measures the system-prompt tokens (MCP tool schemas,
  plugins, built-ins) re-sent on EVERY turn, and what you can reclaim.
- **chaser-context-diet** — applies the free, reversible "context diet"
  (deferred tool loading + deny rules) to `settings.json`, with automatic backup.

## Install

**Via the skills CLI (Claude Code, Cursor, and 20+ agents) :**

```
npx skills add HQU-kenaxvi/chaser-lite
```

**Via the Claude Code plugin marketplace :**

```
/plugin marketplace add HQU-kenaxvi/chaser-lite
/plugin install chaser-lite@chaser
```

The plugin exposes `/chaser-lite:audit` and `/chaser-lite:regime` (+ `retirer`
to undo).

## Structure

```
skills/                          ← standalone skills (skills.sh / npx skills)
  chaser-cost-audit/SKILL.md + audit.py
  chaser-context-diet/SKILL.md + regime_lite.py
.claude-plugin/marketplace.json  ← plugin marketplace catalogue
plugins/chaser-lite/             ← Claude Code plugin (same tools, /commands)
```

## Honest by design

Numbers are labeled as estimates, nothing is ever sent off your machine, and
every change is reversible with one command. The full product — orchestration
engine that routes work to cheaper models, budget guard, eco chat, persistent
memory, Cockpit dashboard, security Shield — is **Chaser Pro** :
https://chaser-orchestrator.com · kencaroly@gmail.com
