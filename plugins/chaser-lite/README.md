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
| `/chaser-lite:integrer` | Étend le compresseur aux **autres agents** : Cursor & Gemini CLI (hooks officiels, deny-with-suggestion), Windsurf, Cline, Codex, Kimi (fichiers de règles). Posé par projet, **réversible** via `/chaser-lite:integrer retirer`. |
| `/chaser-lite:compresser` | Branche le **compresseur de sorties** : les commandes verbeuses (tests, lint, git, find/tree) sont compressées avant d'entrer dans le contexte — **signaux d'erreur préservés, jamais de troncature aveugle**. Habitudes `rtk` compatibles (préfixe absorbé). Réversible via `/chaser-lite:compresser retirer`. |

Après `/chaser-lite:regime`, **redémarre Claude Code** puis compare avec `/context`.

## Skills bonus (qualité de dev)

Deux skills éprouvés, chargés **au bon moment** par le modèle (ou invocables à la
main). Ils ne modifient aucun réglage et n'envoient rien — ils orientent seulement
le raisonnement de Claude :

| Skill | Ce qu'il fait |
|---|---|
| `systematic-debugging` | Face à un bug/échec de test, impose de **trouver la cause racine avant tout correctif** (4 phases, loi de fer « pas de fix sans investigation »). Fini les rustines qui masquent le problème. |
| `verification-before-completion` | Avant d'annoncer « c'est bon / corrigé / ça passe », impose de **relancer la vérification et lire la sortie**. Preuve avant tout claim. |

*Adaptés de [obra/superpowers](https://github.com/obra/superpowers) (MIT) — voir `THIRD-PARTY-NOTICES.md`.*

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

→ **https://chaser-orchestrator.com/en.html** · kencaroly@gmail.com

*© 2026 Ken Caroly. Chaser Lite est fourni gratuitement « en l'état ». Composants
tiers sous licence MIT : voir `THIRD-PARTY-NOTICES.md`.*
