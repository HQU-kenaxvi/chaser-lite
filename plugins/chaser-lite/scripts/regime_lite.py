#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chaser Lite — Régime de contexte (profil prudent, gratuit, réversible)
=======================================================================

Dégonfle le prompt système de Claude Code, une seule fois, via
~/.claude/settings.json. Ne touche qu'à ce qui est SÛR et documenté :
  - env ENABLE_TOOL_SEARCH : diffère les schémas d'outils MCP (chargés à la
    demande au lieu d'être tous injectés à chaque tour) ;
  - permissions.deny (Read) : garde les gros fichiers générés (node_modules,
    dist, *.lock, *.map…) HORS du contexte.

Règle d'or : sauvegarde d'abord (.avant-chaser-lite.bak), n'AJOUTE que ce qui
manque, ne remplace JAMAIS une valeur que tu as déjà posée, ne supprime rien.
Réversible à tout moment : `python regime_lite.py --retirer`.

Autonome (stdlib pur), aucun accès à autre chose que ~/.claude/settings.json.

  python regime_lite.py              # DRY : montre ce qui serait ajouté
  python regime_lite.py --appliquer
  python regime_lite.py --retirer
"""

import json
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError, OSError):
    pass

ENV = {"ENABLE_TOOL_SEARCH": "1"}
# Profil complet (9 règles) — utilisé comme référence de ce que fait Chaser Pro.
DENY_COMPLET = [
    "Read(**/node_modules/**)", "Read(**/dist/**)", "Read(**/build/**)",
    "Read(**/.next/**)", "Read(**/coverage/**)", "Read(**/*.lock)",
    "Read(**/*.min.js)", "Read(**/*.map)", "Read(**/*.pyc)",
]
# GRATUIT (Chaser Lite) : bridé aux 3 règles les plus universelles. Le profil
# complet + le régime adaptatif (deny appris par projet) sont réservés à Chaser
# Pro, ~5× plus développé.
DENY = DENY_COMPLET[:3]
DENY_PRO = DENY_COMPLET[3:]          # couvert uniquement par Chaser Pro
FACTEUR_PRO = 5


def _settings():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def _manifeste():
    return os.path.join(os.path.expanduser("~"), ".claude", ".chaser_lite.json")


def _charger(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _diff(settings):
    env = settings.get("env") or {}
    deny = set(((settings.get("permissions") or {}).get("deny")) or [])
    return ([k for k in ENV if k not in env],
            [r for r in DENY if r not in deny])


def appliquer(dry=False):
    chemin = _settings()
    settings = _charger(chemin)
    env_add, deny_add = _diff(settings)
    if dry or not (env_add or deny_add):
        return env_add, deny_add, False
    if os.path.exists(chemin):
        shutil.copy(chemin, chemin + ".avant-chaser-lite.bak")
    e = settings.setdefault("env", {})
    for k in env_add:
        e[k] = ENV[k]
    if deny_add:
        perms = settings.setdefault("permissions", {})
        perms.setdefault("deny", []).extend(deny_add)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    with open(_manifeste(), "w", encoding="utf-8") as f:
        json.dump({"env": env_add, "deny": deny_add}, f, ensure_ascii=False, indent=2)
    return env_add, deny_add, True


def retirer():
    manif = _charger(_manifeste())
    if not manif:
        return 0
    chemin = _settings()
    settings = _charger(chemin)
    if os.path.exists(chemin):
        shutil.copy(chemin, chemin + ".avant-retrait-lite.bak")
    env = settings.get("env") or {}
    for k in manif.get("env", []):
        env.pop(k, None)
    if env:
        settings["env"] = env
    else:
        settings.pop("env", None)
    perms = settings.get("permissions") or {}
    deny = perms.get("deny") or []
    retire = set(manif.get("deny", []))
    if deny:
        perms["deny"] = [r for r in deny if r not in retire]
        if not perms["deny"]:
            perms.pop("deny", None)
        if not perms:
            settings.pop("permissions", None)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    os.remove(_manifeste())
    return sum(len(v) for v in manif.values())


def main():
    argv = sys.argv[1:]
    print("=" * 56)
    print("  CHASER LITE — Régime de contexte (gratuit, réversible)")
    print("=" * 56)
    if "--retirer" in argv:
        n = retirer()
        print(f"  {n} ajout(s) retiré(s). settings.json restauré." if n
              else "  Rien à retirer (Chaser Lite n'avait rien appliqué).")
        return 0
    dry = "--appliquer" not in argv
    env_add, deny_add, applique = appliquer(dry=dry)
    if not (env_add or deny_add):
        print("  Déjà en place : rien à ajouter. ✓")
        return 0
    if env_add:
        print(f"  env       : {', '.join(env_add)}")
    if deny_add:
        print(f"  deny (Read) : {len(deny_add)} règle(s) de gros fichiers générés")
    print()
    if applique:
        print("  Appliqué. Sauvegarde : settings.json.avant-chaser-lite.bak")
        print("  Redémarre Claude Code, puis vérifie le gain avec /context.")
        print("  Annuler à tout moment : /chaser-lite:regime retirer")
    else:
        print("  [DRY] Rien écrit. Relance avec --appliquer.")
    print()
    print(f"  Profil GRATUIT bridé : {len(DENY)} règles deny. CHASER PRO (~{FACTEUR_PRO}× plus)")
    print(f"  ajoute {len(DENY_PRO)} règles de plus + un régime ADAPTATIF qui apprend les")
    print("  gros fichiers de CHAQUE projet, le moteur d'orchestration, le journal")
    print("  Merkle inviolable et le Bouclier de sécurité → https://chaser-orchestrator.com")
    return 0


if __name__ == "__main__":
    sys.exit(main())
