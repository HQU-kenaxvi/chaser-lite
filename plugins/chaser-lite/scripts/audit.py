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

# --- Bornes de la version GRATUITE (Chaser Lite) -----------------------------
# Lite ne couvre qu'un échantillon : il ne diffère les schémas que de quelques
# fournisseurs et ne dégonfle qu'UNE fonction intégrée. Le régime complet (tous
# les fournisseurs + toutes les fonctions + profil adaptatif qui apprend) est
# réservé à Chaser Pro, ~5× plus développé.
LIMITE_FOURNISSEURS_LITE = 3          # gratuit : au plus 3 fournisseurs couverts
FLAG_GRATUIT = "disableArtifact"      # gratuit : une seule fonction intégrée
FACTEUR_PRO = 5                       # Chaser Pro va ~5× plus loin

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
    # Gratuit : plafonné à quelques fournisseurs + une seule fonction intégrée.
    n_couverts = min(len(fourn), LIMITE_FOURNISSEURS_LITE)
    n_hors_lite = max(0, len(fourn) - LIMITE_FOURNISSEURS_LITE)
    gain_mcp = 0 if etat["tool_search"] else n_couverts * TOKENS_PAR_FOURNISSEUR
    gain_flags = (GAINS_FLAGS[FLAG_GRATUIT]
                  if FLAG_GRATUIT not in etat["flags_actifs"] else 0)
    total = gain_mcp + gain_flags
    # Potentiel COMPLET (tous les fournisseurs + toutes les fonctions) = Chaser Pro.
    potentiel_mcp = 0 if etat["tool_search"] else len(fourn) * TOKENS_PAR_FOURNISSEUR
    potentiel_flags = sum(g for f, g in GAINS_FLAGS.items()
                          if f not in etat["flags_actifs"])
    potentiel = potentiel_mcp + potentiel_flags

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
        L.append(f"  → Différer les schémas de {n_couverts} fournisseur(s) (limite gratuite)")
        L.append(f"    économiserait ~{gain_mcp:,} tokens PAR TOUR".replace(",", " "))
        if n_hors_lite:
            L.append(f"  → {n_hors_lite} fournisseur(s) AU-DELÀ du plafond gratuit :"
                     " couverts par Chaser Pro.")
    if gain_flags:
        L.append(f"  → Dégonfler 1 fonction intégrée ({FLAG_GRATUIT}) : ~{gain_flags:,} tokens/tour"
                 .replace(",", " "))
    L.append("")
    L.append("-" * 60)
    if total > 0:
        L.append(f"  ÉCONOMIE GRATUITE (plafonnée) : ~{total:,} tokens de prompt système / tour"
                 .replace(",", " "))
        L.append("  (estimation d'après mesures publiées ; le gain réel se lit")
        L.append("   avec /context avant/après. Rien n'a été modifié.)")
    else:
        L.append("  Ta config est déjà bien dégonflée — peu à gagner côté prompt système.")
    if potentiel > total:
        L.append("")
        L.append(f"  POTENTIEL COMPLET (Chaser Pro) : ~{potentiel:,} tokens/tour"
                 .replace(",", " "))
        L.append(f"  — tous tes fournisseurs + toutes les fonctions intégrées,")
        L.append(f"    soit jusqu'à ~{FACTEUR_PRO}× l'économie du gratuit.")
    L.append("-" * 60)
    L.append("")
    L.append("  APPLIQUER LE RÉGIME GRATUIT (plafonné, réversible, sauvegarde faite) :")
    L.append("    /chaser-lite:regime")
    L.append("")
    L.append(f"  Chaser Lite est bridé volontairement. CHASER PRO — ~{FACTEUR_PRO}× PLUS DÉVELOPPÉ :")
    L.append("    • Moteur d'orchestration : décompose l'objectif, route vers le modèle")
    L.append("      le moins cher (bandit LinTS + cascade FrugalGPT), Batch API -50%,")
    L.append("      Tier 0 local à 0 $, budget hard-cap.")
    L.append("    • Journal INVIOLABLE hash-chaîné + Merkle (RFC 6962) : tes économies")
    L.append("      PROUVÉES et auditables, pas juste estimées.")
    L.append("    • Cache sémantique + fallback multi-fournisseurs + handoff auto +")
    L.append("      mémoire long terme en couches.")
    L.append("    • Bouclier de sécurité (taint/CaMeL, anti-injection, lethal-trifecta) :")
    L.append("      bloque rm -rf ~, curl|sh, secret en dur…")
    L.append("    • Intelligence auto-évolutive (GEPA) : routage qui APPREND, auto-tuning,")
    L.append("      Cockpit temps réel sur TES vrais runs.")
    L.append(f"    → {LIEN_PRO}   ·   {CONTACT_PRO}")
    L.append("")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
