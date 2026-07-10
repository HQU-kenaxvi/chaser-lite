# Chaser — Marketplace de plugins Claude Code

Marketplace officiel de **Chaser**, l'outil qui réduit le coût de Claude Code
(abonnement + clé API), 100 % local.

## Plugin disponible

- **chaser-lite** — audit du coût caché + régime de contexte. Gratuit.

## Installation (pour les utilisateurs)

```
/plugin marketplace add caroly-chaser/chaser-lite
/plugin install chaser-lite@chaser
```

*(remplace `caroly-chaser/chaser-lite` par le chemin de ton dépôt GitHub une fois publié)*

## Structure

```
.claude-plugin/
  marketplace.json          ← catalogue (liste chaser-lite)
plugins/
  chaser-lite/
    .claude-plugin/plugin.json
    skills/audit/SKILL.md    ← /chaser-lite:audit
    skills/regime/SKILL.md   ← /chaser-lite:regime
    scripts/audit.py         ← audit local (lecture seule)
    scripts/regime_lite.py   ← régime réversible
    README.md
```

## Publier

1. `git init && git add . && git commit -m "Chaser Lite v1"`
2. Créer un repo GitHub public (ex. `caroly-chaser/chaser-lite`) et `git push`.
3. Les utilisateurs ajoutent le marketplace avec la commande ci-dessus.
4. (Optionnel) Soumettre au marketplace communautaire :
   https://platform.claude.com/plugins/submit

## À personnaliser avant publication

- `plugins/chaser-lite/scripts/audit.py` : `LIEN_PRO` (ton lien de vente Chaser Pro).
- README : le chemin du dépôt GitHub.
