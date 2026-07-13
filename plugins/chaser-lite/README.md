# Chaser Lite

**Réduis le coût de Claude Code. Gratuit, 100 % local, zéro dépendance.**

Claude Code te coûte silencieusement des tokens à chaque message : les schémas
d'outils (serveurs MCP + plugins) et les fonctions intégrées sont re-envoyés dans
le prompt système **à chaque tour**. Chaser Lite le mesure et le dégonfle.

## Commandes

| Commande | Ce qu'elle fait |
|---|---|
| `/chaser-lite:audit` | Mesure, sur ta machine, combien de tokens de prompt système sont gaspillés à chaque tour, et l'économie possible. **Lecture seule, rien n'est modifié, rien n'est envoyé.** |
| `/chaser-lite:regime` | Applique le régime de contexte (ENABLE_TOOL_SEARCH + deny des gros fichiers) dans `~/.claude/settings.json`. **Sauvegarde automatique, réversible** via `/chaser-lite:regime retirer`. |

Après `/chaser-lite:regime`, **redémarre Claude Code** puis compare avec `/context`.

## Installation

```
/plugin marketplace add HQU-kenaxvi/chaser-lite     # (ton repo GitHub)
/plugin install chaser-lite@chaser
```

Prérequis : Python 3 (déjà présent sur la plupart des machines de dev).

## Confidentialité

Tout est local. Aucune donnée, aucune clé, aucun prompt ne quitte ta machine.
Le régime n'écrit que dans `~/.claude/settings.json`, après sauvegarde, et se
retire proprement.

## Passer à la version complète — Chaser Pro

Chaser Lite ne fait que l'audit + le régime de contexte. **Chaser Pro** ajoute :

- **Moteur d'orchestration** : décompose un objectif, route vers le modèle le
  moins cher (Haiku/Sonnet), Batch API −50 %, budget hard cap.
- **Chat éco** + **cache 1h** + **handoff automatique** entre sessions + **mémoire
  long terme**.
- **Bouclier de sécurité** : bloque `rm -rf ~`, `curl | sh`, secret écrit en dur…
- **Cockpit** : tes économies mesurées **en temps réel** sur tes vrais runs.
- **Intelligence** : routage qui apprend, auto-tuning des réglages.

→ **https://chaser-orchestrator.com** · kencaroly@gmail.com

*© 2026 Ken Caroly. Chaser Lite est fourni gratuitement « en l'état ».*
