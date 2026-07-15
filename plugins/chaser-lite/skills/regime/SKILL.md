---
description: Applique le régime de contexte de Chaser (gratuit, réversible) — dégonfle le prompt système de Claude Code via settings.json (ENABLE_TOOL_SEARCH + deny des gros fichiers). Sauvegarde faite. Argument "retirer" pour annuler.
disable-model-invocation: true
---

# Chaser Lite — Régime de contexte (gratuit)

But : réduire les tokens re-envoyés à chaque tour, en une écriture réversible de
`~/.claude/settings.json` (sauvegarde automatique).

1. Si l'argument est exactement `retirer` (valeur : "$ARGUMENTS"), lance l'annulation :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/regime_lite.py" --retirer
```

2. Sinon, montre D'ABORD ce qui serait changé (dry-run), puis applique :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/regime_lite.py" --appliquer
```

Si `python` échoue, essaie `python3`. Si `${CLAUDE_PLUGIN_ROOT}` est vide,
localise le dossier de ce plugin (celui contenant `scripts/regime_lite.py`).

Présente la sortie à l'utilisateur **dans SA langue** (le script parle français :
traduis les libellés si l'utilisateur écrit dans une autre langue, en gardant les
chiffres exacts). Rappelle-lui de **redémarrer Claude Code** pour que le changement
prenne effet, et qu'il peut tout annuler avec `/chaser-lite:regime retirer`. Ne modifie rien d'autre que ce que le script fait.
Le profil gratuit est **bridé à quelques règles** ; le profil complet adaptatif et
le moteur (journal Merkle, cache sémantique, Bouclier) sont dans **Chaser Pro,
~5× plus développé** — https://chaser-orchestrator.com/en.html
