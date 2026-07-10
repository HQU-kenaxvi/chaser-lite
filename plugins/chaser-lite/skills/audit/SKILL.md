---
description: Audite le coût caché de Claude Code sur cette machine — combien de tokens de prompt système (schémas d'outils MCP + plugins) sont re-envoyés à chaque tour, et combien on peut en économiser. 100% local, lecture seule.
disable-model-invocation: true
---

# Chaser Lite — Audit du coût caché

Exécute le script d'audit local (aucune donnée ne quitte la machine, lecture seule) :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py"
```

Si `python` échoue, essaie `python3`. Si le chemin est vide (variable non résolue),
localise le dossier de ce plugin (celui qui contient `scripts/audit.py`) et lance
le script depuis là.

Ensuite, présente la sortie du script à l'utilisateur **telle quelle** (elle est déjà
formatée et honnête : les chiffres sont étiquetés comme des estimations). N'invente
aucun chiffre, ne promets pas de pourcentage — reprends uniquement ce que le script
a mesuré. Termine en rappelant qu'il peut appliquer le régime gratuitement avec
`/chaser-lite:regime`.
