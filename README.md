# Chaser Lite — cut the hidden cost of Claude Code

Free tools from **Chaser** (https://chaser-orchestrator.com/en.html) that measure and
shrink the token cost of your Claude Code setup. 100% local, read-only audit,
reversible changes, zero dependencies (Python stdlib only).

- **chaser-cost-audit** — measures the system-prompt tokens (MCP tool schemas,
  plugins, built-ins) re-sent on EVERY turn, and what you can reclaim. The free
  tier is intentionally capped (a sample of tool providers + one built-in flag);
  the full potential is shown as the Chaser Pro figure.
- **chaser-context-diet** — applies the free, reversible "context diet"
  (deferred tool loading + a capped set of deny rules) to `settings.json`, with
  automatic backup.

> Chaser Lite is **deliberately throttled** so it stays simple and safe. The
> economy and the toolset are limited on purpose — **Chaser Pro is ~5× more
> developed** (see below).

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
every change is reversible with one command.

## Chaser Pro — ~5× more developed

Lite audits and shrinks the system prompt, capped. **Chaser Pro** is the full
engine:

- **Orchestration engine** — decomposes a goal and routes each step to the
  cheapest model (LinTS bandit + FrugalGPT cascade), Batch API −50%, local Tier 0
  at $0, hard budget cap.
- **Tamper-proof savings** — hash-chained + Merkle (RFC 6962) journal: your
  savings are *proven and auditable*, not just estimated.
- **Semantic cache + multi-provider fallback + auto handoff + layered long-term
  memory.**
- **Security Shield** (taint/CaMeL, prompt-injection & lethal-trifecta guards) —
  blocks `rm -rf ~`, `curl | sh`, hard-coded secrets…
- **Self-evolving intelligence (GEPA)** — a router that *learns*, auto-tuning, and
  a real-time Cockpit on your actual runs.

→ **https://chaser-orchestrator.com/en.html** · kencaroly@gmail.com
