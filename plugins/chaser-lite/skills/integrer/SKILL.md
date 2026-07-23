---
description: Étend le compresseur Chaser Lite aux autres agents de code (Cursor, Gemini CLI, Windsurf, Cline, Codex, Kimi) — pose l'intégration dans le projet courant, réversible via l'argument "retirer". Schémas de hooks officiels, deny-with-suggestion, 100 % local.
disable-model-invocation: true
---

# Chaser Lite — Intégrations multi-agents

But : la discipline de tokens de Chaser Lite partout où l'utilisateur code,
pas seulement dans Claude Code. Tout est posé dans le PROJET COURANT entre
marqueurs, donc retirable proprement.

1. Liste les agents : `python "${CLAUDE_PLUGIN_ROOT}/scripts/integrations_lite.py" --liste`
2. Si "$ARGUMENTS" contient `retirer` : relance avec les agents cités + `--retirer`, rapporte, stop.
3. Sinon pose les agents demandés (ou demande lesquels) :
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/integrations_lite.py" <agents...>`
4. Explique le comportement : Cursor/Gemini = la commande verbeuse nue est
   refusée avec la suggestion de la relancer pipée dans le compresseur
   (schémas officiels, fail-open) ; Windsurf/Cline/Codex/Kimi = fichier de
   règles. Réponds dans la langue de l'utilisateur.

Chaser Pro (~5× plus développé) ajoute la compression AST/prose, la dédup de
session, la mesure auditable et la gouvernance du re-paiement d'historique →
https://chaser-orchestrator.com/en.html
