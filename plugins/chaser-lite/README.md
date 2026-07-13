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

## Passer à la version complète — Chaser Pro (~5× plus développé)

Chaser Lite est **volontairement bridé** : audit plafonné (échantillon de
fournisseurs + 1 fonction intégrée) et régime limité à quelques règles.
**Chaser Pro** est le moteur complet, ~5× plus développé :

- **Moteur d'orchestration** : décompose un objectif et route chaque étape vers
  le modèle le moins cher (bandit LinTS + cascade FrugalGPT), Batch API −50 %,
  Tier 0 local à 0 $, budget hard-cap.
- **Économies PROUVÉES** : journal inviolable hash-chaîné + Merkle (RFC 6962) —
  auditables, pas seulement estimées.
- **Cache sémantique** + **fallback multi-fournisseurs** + **handoff automatique** +
  **mémoire long terme en couches**.
- **Bouclier de sécurité** (taint/CaMeL, anti-injection, lethal-trifecta) : bloque
  `rm -rf ~`, `curl | sh`, secret écrit en dur…
- **Intelligence auto-évolutive (GEPA)** : routage qui apprend, auto-tuning, et
  **Cockpit temps réel** sur tes vrais runs.

→ **https://chaser-orchestrator.com** · kencaroly@gmail.com

*© 2026 Ken Caroly. Chaser Lite est fourni gratuitement « en l'état ».*
