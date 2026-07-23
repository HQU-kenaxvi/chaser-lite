#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chaser Lite — Intégrations multi-agents (gratuit, réversible)
==============================================================

Étend le compresseur de sorties aux autres agents de code. Deux familles :

  HOOKS (schémas officiels vérifiés 23/07/2026) :
    cursor   -> .cursor/hooks.json, événement beforeShellExecution.
                Cursor ne permet PAS de réécrire une commande : le hook fait
                du DENY-WITH-SUGGESTION — la commande verbeuse nue est
                refusée avec le message « relance-la pipée dans le
                compresseur », l'agent réessaie pipé. Fail-open sinon.
    gemini   -> .gemini/settings.json, événement BeforeTool (matcher outil
                shell). Exit 2 + raison sur stderr = même patron.

  FICHIERS DE RÈGLES (l'agent lit des instructions) :
    windsurf -> .windsurfrules        cline -> .clinerules
    codex    -> AGENTS.md             kimi  -> AGENTS.md
    agents   -> AGENTS.md générique

Tout est posé DANS LE PROJET COURANT, entre marqueurs « Chaser Lite », donc
retirable proprement (`--retirer <agent>`). Rien d'envoyé nulle part.

  python integrations_lite.py cursor            # pose l'intégration Cursor
  python integrations_lite.py windsurf --retirer
  python integrations_lite.py --liste
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError, OSError):
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
COMPRESSEUR = os.path.join(ICI, "compresseur_lite.py").replace("\\", "/")
MARQUE_DEBUT = "# --- Chaser Lite (debut) ---"
MARQUE_FIN = "# --- Chaser Lite (fin) ---"

sys.path.insert(0, ICI)
from compresseur_lite import VERBEUSES  # noqa: E402 — même gate que le hook Claude Code

REGLES_TEXTE = f"""{MARQUE_DEBUT}
## Token discipline (Chaser Lite)
For commands with verbose output (tests, linters, git status/log/diff,
tree/find, package installs), ALWAYS pipe through the local compressor —
it keeps head, tail and every error signal (FAILED, errors, warnings):

    <command> 2>&1 | python "{COMPRESSEUR}"

Never paste raw outputs longer than ~50 lines into the conversation.
Full output stays recoverable locally. 100% local, nothing leaves the machine.
{MARQUE_FIN}
"""


# ----------------------------------------------------------------------------
# Portes (modes hook appelés PAR les agents)
# ----------------------------------------------------------------------------
def _commande_dans(obj):
    """Cherche récursivement une valeur de commande shell dans le JSON reçu
    (les agents nomment le champ différemment : command, cmd, script...)."""
    if isinstance(obj, dict):
        for k in ("command", "cmd", "script"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        for v in obj.values():
            r = _commande_dans(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _commande_dans(v)
            if r:
                return r
    return None


def _suggestion(cmd):
    cmd = re.sub(r"^rtk\s+", "", cmd)
    return (f'Token-heavy command intercepted by Chaser Lite. Re-run EXACTLY: '
            f'{cmd} 2>&1 | python "{COMPRESSEUR}"  '
            f'(compressed output, error signals preserved)')


def porte_cursor():
    """stdin: JSON beforeShellExecution de Cursor -> stdout: permission JSON."""
    try:
        j = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        j = {}
    cmd = str(j.get("command") or "").strip()
    if cmd and VERBEUSES.match(cmd) and "compresseur_lite" not in cmd:
        print(json.dumps({"permission": "deny",
                          "agent_message": _suggestion(cmd),
                          "user_message": "Chaser Lite : sortie compressée demandée"}))
    else:
        print(json.dumps({"permission": "allow"}))
    return 0


def porte_gemini():
    """stdin: JSON BeforeTool de Gemini CLI. Exit 2 + raison stderr = bloqué."""
    try:
        j = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        j = {}
    cmd = _commande_dans(j)
    if cmd and VERBEUSES.match(cmd) and "compresseur_lite" not in cmd:
        sys.stderr.write(_suggestion(cmd))
        return 2
    print("{}")
    return 0


# ----------------------------------------------------------------------------
# Poseurs / retireurs par agent (dans le PROJET COURANT)
# ----------------------------------------------------------------------------
def _poser_bloc(chemin, texte=REGLES_TEXTE):
    contenu = ""
    if os.path.exists(chemin):
        contenu = open(chemin, encoding="utf-8").read()
        if MARQUE_DEBUT in contenu:
            return False
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(("\n" if contenu and not contenu.endswith("\n") else "") + texte)
    return True


def _retirer_bloc(chemin):
    if not os.path.exists(chemin):
        return False
    contenu = open(chemin, encoding="utf-8").read()
    if MARQUE_DEBUT not in contenu:
        return False
    avant, _, reste = contenu.partition(MARQUE_DEBUT)
    _, _, apres = reste.partition(MARQUE_FIN)
    nettoye = (avant.rstrip() + "\n" + apres.lstrip("\n")).strip()
    if nettoye:
        open(chemin, "w", encoding="utf-8").write(nettoye + "\n")
    else:
        os.remove(chemin)
    return True


def poser_cursor(retirer=False):
    dossier = os.path.join(".cursor")
    chemin = os.path.join(dossier, "hooks.json")
    d = {}
    if os.path.exists(chemin):
        try:
            d = json.load(open(chemin, encoding="utf-8"))
        except ValueError:
            d = {}
    hooks = d.setdefault("hooks", {})
    entrees = hooks.setdefault("beforeShellExecution", [])
    notres = [e for e in entrees if "integrations_lite" in json.dumps(e)]
    if retirer:
        if not notres:
            return False
        hooks["beforeShellExecution"] = [e for e in entrees if e not in notres]
        if not hooks["beforeShellExecution"]:
            hooks.pop("beforeShellExecution")
    else:
        if notres:
            return False
        d.setdefault("version", 1)
        entrees.append({
            "command": f'python "{os.path.join(ICI, "integrations_lite.py")}" --porte-cursor',
            "timeout": 10})
    os.makedirs(dossier, exist_ok=True)
    json.dump(d, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return True


def poser_gemini(retirer=False):
    dossier = os.path.join(".gemini")
    chemin = os.path.join(dossier, "settings.json")
    d = {}
    if os.path.exists(chemin):
        try:
            d = json.load(open(chemin, encoding="utf-8"))
        except ValueError:
            d = {}
    hooks = d.setdefault("hooks", {})
    entrees = hooks.setdefault("BeforeTool", [])
    notres = [e for e in entrees if "integrations_lite" in json.dumps(e)]
    if retirer:
        if not notres:
            return False
        hooks["BeforeTool"] = [e for e in entrees if e not in notres]
        if not hooks["BeforeTool"]:
            hooks.pop("BeforeTool")
    else:
        if notres:
            return False
        entrees.append({
            "type": "command",
            "command": f'python "{os.path.join(ICI, "integrations_lite.py")}" --porte-gemini',
            "matcher": "run_shell_command|run_terminal_command|shell|execute.*",
            "timeout": 10000})
    os.makedirs(dossier, exist_ok=True)
    json.dump(d, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return True


AGENTS = {
    "cursor": ("hook beforeShellExecution (deny-with-suggestion)", poser_cursor),
    "gemini": ("hook BeforeTool (exit 2 + suggestion)", poser_gemini),
    "windsurf": (".windsurfrules", lambda r=False: (_retirer_bloc if r else _poser_bloc)(".windsurfrules")),
    "cline": (".clinerules", lambda r=False: (_retirer_bloc if r else _poser_bloc)(".clinerules")),
    "codex": ("AGENTS.md", lambda r=False: (_retirer_bloc if r else _poser_bloc)("AGENTS.md")),
    "kimi": ("AGENTS.md", lambda r=False: (_retirer_bloc if r else _poser_bloc)("AGENTS.md")),
    "agents": ("AGENTS.md générique", lambda r=False: (_retirer_bloc if r else _poser_bloc)("AGENTS.md")),
}


def main():
    argv = sys.argv[1:]
    if "--porte-cursor" in argv:
        return porte_cursor()
    if "--porte-gemini" in argv:
        return porte_gemini()
    cibles = [a for a in argv if a in AGENTS]
    if "--liste" in argv or not cibles:
        print("Agents supportés :", ", ".join(sorted(AGENTS)))
        print("Usage : python integrations_lite.py <agent> [--retirer]")
        print("(posé dans le PROJET COURANT, réversible, marqueurs Chaser Lite)")
        return 0
    retirer = "--retirer" in argv
    for a in cibles:
        desc, poseur = AGENTS[a]
        fait = poseur(retirer)
        verbe = "retiré de" if retirer else "posé pour"
        print(f"  {'OK ' if fait else '=  '} {a} ({desc}) : "
              f"{verbe + ' ce projet' if fait else 'déjà en place / rien à faire'}")
    if not retirer:
        print("\n  Chaser Pro (~5× plus) : compression AST/prose, dédup, mesure "
              "auditable, gouvernance du re-paiement d'historique — "
              "chaser-orchestrator.com/en.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
