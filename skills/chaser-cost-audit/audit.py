#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chaser Lite — Audit du coût caché de Claude Code (100% local, 0 $, lecture seule)
==================================================================================

Mesure, SUR CETTE MACHINE, ce que Claude Code te coûte silencieusement à chaque
tour : les schémas d'outils MCP + plugins + fonctions intégrées re-envoyés dans
le prompt système à CHAQUE message. Puis estime ce que le régime de contexte
peut en économiser.

Aucune donnée ne quitte la machine. Aucune modification (lecture seule).
Chiffres = mesures publiées (firecrawl / aihero / scottspence), étiquetés comme
estimations — jamais une promesse.
"""

import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError, OSError):
    pass

# ~10 000 tokens de schémas différables par fournisseur d'outils (fourchette
# publiée 10-20k ; on reste bas, honnête).
TOKENS_PAR_FOURNISSEUR = 10000
# Fonctions intégrées désactivables (defs re-envoyées chaque tour) — ordre de grandeur.
GAINS_FLAGS = {"disableWorkflows": 5300, "disableBundledSkills": 3000,
               "disableArtifact": 1200}

# >>> À PERSONNALISER par le vendeur : lien de la page Chaser Pro <<<
LIEN_PRO = "https://chaser-orchestrator.com"          # page de vente Chaser Pro
CONTACT_PRO = "kencaroly@gmail.com"


def _charger(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def fournisseurs_outils():
    """Compte les serveurs MCP + plugins actifs = fournisseurs de schémas d'outils."""
    home = os.path.expanduser("~")
    noms = set()
    cfg = _charger(os.path.join(home, ".claude.json"))
    bloc = cfg.get("mcpServers")
    if isinstance(bloc, dict):
        noms.update(bloc.keys())
    projets = cfg.get("projects")
    if isinstance(projets, dict):
        for infos in projets.values():
            b = (infos or {}).get("mcpServers")
            if isinstance(b, dict):
                noms.update(b.keys())
    st = _charger(os.path.join(home, ".claude", "settings.json"))
    val = st.get("enabledMcpjsonServers")
    if isinstance(val, list):
        noms.update(str(x) for x in val)
    ep = st.get("enabledPlugins")
    if isinstance(ep, dict):
        noms.update(k for k, v in ep.items() if v)
    elif isinstance(ep, list):
        noms.update(str(x) for x in ep)
    return sorted(noms)


def deja_optimise():
    """Le régime est-il déjà (partiellement) actif chez cet utilisateur ?"""
    st = _charger(os.path.join(os.path.expanduser("~"), ".claude", "settings.json"))
    env = st.get("env") or {}
    return {
        "tool_search": env.get("ENABLE_TOOL_SEARCH") in ("1", "auto", "true", True),
        "flags_actifs": [f for f in GAINS_FLAGS if st.get(f) is True],
        "deny": len(((st.get("permissions") or {}).get("deny")) or []),
    }


def main():
    fourn = fournisseurs_outils()
    etat = deja_optimise()
    gain_mcp = 0 if etat["tool_search"] else len(fourn) * TOKENS_PAR_FOURNISSEUR
    gain_flags = sum(g for f, g in GAINS_FLAGS.items() if f not in etat["flags_actifs"])
    total = gain_mcp + gain_flags

    L = []
    L.append("=" * 60)
    L.append("  CHASER LITE — audit du coût caché de Claude Code")
    L.append("  (100% local · lecture seule · aucune donnée envoyée)")
    L.append("=" * 60)
    L.append("")
    L.append(f"  Fournisseurs d'outils détectés (serveurs MCP + plugins) : {len(fourn)}")
    if fourn:
        apercu = ", ".join(fourn[:8]) + (" …" if len(fourn) > 8 else "")
        L.append(f"    {apercu}")
    L.append("")
    L.append("  Chaque fournisseur injecte le schéma complet de ses outils dans le")
    L.append("  prompt système, RE-ENVOYÉ à chaque message de la session. C'est le")
    L.append("  coût caché n°1 de l'abonnement Claude Code.")
    L.append("")
    if etat["tool_search"]:
        L.append("  ✓ ENABLE_TOOL_SEARCH est DÉJÀ actif : les schémas sont différés. Bien joué.")
    else:
        L.append(f"  → Différer ces schémas (ENABLE_TOOL_SEARCH) économiserait")
        L.append(f"    ~{gain_mcp:,} tokens PAR TOUR".replace(",", " "))
    if gain_flags:
        L.append(f"  → Désactiver les fonctions intégrées inutiles : ~{gain_flags:,} tokens/tour"
                 .replace(",", " "))
    L.append("")
    L.append("-" * 60)
    if total > 0:
        L.append(f"  ÉCONOMIE ESTIMÉE : ~{total:,} tokens de prompt système PAR TOUR"
                 .replace(",", " "))
        L.append("  (estimation d'après mesures publiées ; le gain réel se lit")
        L.append("   avec /context avant/après. Rien n'a été modifié.)")
    else:
        L.append("  Ta config est déjà bien dégonflée — peu à gagner côté prompt système.")
    L.append("-" * 60)
    L.append("")
    L.append("  APPLIQUER LE RÉGIME GRATUITEMENT (réversible, sauvegarde faite) :")
    L.append("    /chaser-lite:regime")
    L.append("")
    L.append("  Chaser Lite ne fait QUE ça. La version complète Chaser Pro ajoute :")
    L.append("    • Moteur d'orchestration (route vers le modèle le moins cher, Batch -50%)")
    L.append("    • Chat éco + cache 1h + handoff auto entre sessions + mémoire long terme")
    L.append("    • Bouclier de sécurité (bloque rm -rf ~, curl|sh, secret en dur…)")
    L.append("    • Cockpit : économies mesurées EN TEMPS RÉEL sur TES runs")
    L.append("    • Intelligence : routage qui apprend, auto-tuning des réglages")
    L.append(f"    → {LIEN_PRO}   ·   {CONTACT_PRO}")
    L.append("")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
