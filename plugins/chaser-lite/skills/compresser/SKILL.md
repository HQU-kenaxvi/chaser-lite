---
description: Branche le compresseur de sorties de Chaser Lite (gratuit, réversible) — les grosses sorties de commandes verbeuses (tests, lint, git, find/tree) sont compressées AVANT d'entrer dans le contexte, signaux d'erreur préservés. Argument "retirer" pour annuler. Compatible habitudes rtk (préfixe absorbé).
disable-model-invocation: true
---

# Chaser Lite — Compresseur de sorties (gratuit)

But : le token le moins cher est celui qui n'entre jamais dans le contexte.
Un hook PreToolUse re-pipe les commandes verbeuses vers un compresseur local
(stdlib pur, 0 réseau) qui garde la tête, la queue et TOUTES les lignes de
signal (erreurs, FAILED, warnings) — jamais de troncature aveugle.

1. Si l'argument est exactement `retirer` (valeur : "$ARGUMENTS"), lance :
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/compresseur_lite.py" --retirer`
   puis rapporte le résultat et arrête-toi.

2. Sinon, montre d'abord le DRY :
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/compresseur_lite.py" --dry`

3. Demande confirmation à l'utilisateur, puis applique :
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/compresseur_lite.py" --appliquer`

4. Rappelle : redémarrer Claude Code pour activer le hook ; annulation à tout
   moment via `/chaser-lite:compresser retirer` ; sauvegarde automatique de
   settings.json. Réponds dans la langue de l'utilisateur.

Version gratuite bridée aux familles universelles (tests, lint, git,
exploration). Chaser Pro (~5× plus développé) compresse ~60 familles
(aws, kubectl, docker, terraform…), le CODE (carte AST), la PROSE (saillance),
déduplique la session entière et MESURE le gain (holdout 10 %, journal
auditable) → https://chaser-orchestrator.com/en.html
