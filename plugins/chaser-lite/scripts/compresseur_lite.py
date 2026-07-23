#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chaser Lite — Compresseur de sorties (gratuit, réversible, bridé)
==================================================================

Réduit les grosses sorties de commandes verbeuses AVANT qu'elles n'entrent
dans le contexte de Claude Code — le token le moins cher est celui qu'on
n'envoie pas. Équivalent gratuit et local de la compression d'outils type RTK,
mais intégré à Claude Code (hook PreToolUse) et volontairement BRIDÉ :

  GRATUIT (Chaser Lite) : familles universelles (tests, lint, git, exploration),
    compression générique (git status catégorisé + tête/queue + lignes de
    SIGNAL gardées : erreurs, FAILED, fichiers).
  CHASER PRO (~5× plus développé) : ~60 familles de commandes, compression
    par CODE (carte AST), par PROSE (saillance), dédup de session, lint groupé
    par règle, + MESURE auditable (holdout 10 %, journal scellé).

Deux rôles dans un seul fichier autonome (stdlib pur) :
  - FILTRE : `... 2>&1 | python compresseur_lite.py` compresse le flux reçu.
  - INSTALLEUR : pose/retire un hook PreToolUse dans ~/.claude/settings.json
    (sauvegarde .avant-chaser-lite-compress.bak, manifeste, 100 % réversible).

  python compresseur_lite.py --appliquer   # branche le hook
  python compresseur_lite.py --retirer      # débranche proprement
  echo "..." | python compresseur_lite.py   # (usage interne du hook)
"""
import json
import os
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError, OSError):
    pass

SEUIL = 2500          # en dessous, on ne touche à rien (bruit)
TETE, QUEUE = 40, 25  # lignes gardées en tête / queue quand on tronque
# Lignes de SIGNAL : jamais élaguées, même au milieu d'un gros bloc.
_SIGNAL = re.compile(
    r"\b(error|erreur|fail(ed|ure)?|échec|assert|exception|traceback|"
    r"warning|fatal|panic|refused|denied|cannot|unable|missing|E\d{2,}|"
    r"TS\d{3,}|✗|✘|×|FAILED)\b", re.I)

# GATE bridé : familles verbeuses les plus universelles. Chaser Pro en couvre
# ~60 (aws, kubectl, docker, pulumi, terraform, sbt, golangci-lint...).
VERBEUSES = re.compile(
    r"^(rtk\s+)?("
    r"git (status|log|diff)\b|"
    r"pytest\b|python -m (pytest|unittest)\b|(npm|pnpm|yarn|bun) (run )?test\b|"
    r"npx (jest|vitest)\b|(jest|vitest)\b|go test\b|cargo (test|build|check)\b|"
    r"tsc\b|npx tsc\b|eslint\b|ruff check\b|(npm|pnpm|yarn|bun) (run )?(build|lint)\b|"
    r"(npm|pnpm|yarn|bun) (install|ci)\b|pip3? install\b|"
    r"tree\b|find \S|ls -[a-zA-Z]*R"
    r")")

UPSELL = ("[Chaser Lite — sortie compressée pour économiser des tokens. "
          "Chaser Pro (~5× plus développé) compresse ~60 familles de commandes, "
          "le CODE (carte AST) et la PROSE, déduplique la session et MESURE le "
          "gain (holdout auditable) → chaser-orchestrator.com/en.html]")


# ----------------------------------------------------------------------------
# 1. Le compresseur (filtre de flux)
# ----------------------------------------------------------------------------
def _compacter_git_status(texte):
    """git status verbeux -> compte par catégorie (sans perte d'information
    utile : on garde les noms de fichiers, groupés)."""
    lignes = texte.splitlines()
    if not any("modified:" in l or "new file:" in l or "Untracked files" in l
               for l in lignes):
        return None
    mod = [l.split(":", 1)[1].strip() for l in lignes if "modified:" in l]
    new = [l.split(":", 1)[1].strip() for l in lignes if "new file:" in l]
    unt = [l.strip() for l in lignes
           if l.strip() and l.startswith("\t") and ":" not in l]
    out = ["[Chaser Lite — git status compacté]"]
    if mod:
        out.append(f"  modifiés ({len(mod)}) : " + ", ".join(mod[:20])
                   + (" …" if len(mod) > 20 else ""))
    if new:
        out.append(f"  nouveaux ({len(new)}) : " + ", ".join(new[:20]))
    if unt:
        out.append(f"  non suivis ({len(unt)}) : " + ", ".join(unt[:20]))
    return "\n".join(out)


def compresser(texte):
    """Renvoie le texte compressé (ou l'original si rien à gagner)."""
    if len(texte) < SEUIL:
        return texte
    git = _compacter_git_status(texte)
    if git and len(git) < len(texte):
        return git + "\n" + UPSELL
    lignes = texte.splitlines()
    if len(lignes) <= TETE + QUEUE + 10:
        return texte
    # tête + lignes de signal du milieu + queue
    milieu_signal = [l for l in lignes[TETE:-QUEUE] if _SIGNAL.search(l)]
    caches = len(lignes) - TETE - QUEUE - len(milieu_signal)
    bloc = lignes[:TETE]
    if milieu_signal:
        bloc.append(f"  … [{caches} lignes élaguées ; "
                    f"{len(milieu_signal)} ligne(s) de signal gardée(s)] …")
        bloc.extend(milieu_signal[:40])
    else:
        bloc.append(f"  … [{caches} lignes élaguées] …")
    bloc.extend(lignes[-QUEUE:])
    out = "\n".join(bloc)
    return (out + "\n" + UPSELL) if len(out) < len(texte) else texte


# ----------------------------------------------------------------------------
# 2. L'installeur (hook PreToolUse dans settings.json, réversible)
# ----------------------------------------------------------------------------
def _settings():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def _manifeste():
    return os.path.join(os.path.expanduser("~"), ".claude",
                        ".chaser_lite_compress.json")


def _charger(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _entree_hook():
    """Le hook : un shell qui, pour une commande verbeuse, la re-pipe vers ce
    fichier. `command` pointe vers CE script par chemin absolu."""
    moi = os.path.abspath(__file__).replace("\\", "/")
    return {"type": "command",
            "command": f'python "{moi}" --hook',
            "timeout": 8,
            "statusMessage": "Compression des sorties (Chaser Lite)"}


def appliquer(dry=False):
    chemin = _settings()
    settings = _charger(chemin)
    hooks = settings.get("hooks") or {}
    deja = json.dumps(hooks.get("PreToolUse") or []).find("chaser_lite_compress") >= 0 \
        or json.dumps(hooks.get("PreToolUse") or []).find("compresseur_lite") >= 0
    if deja:
        return False, False
    if dry:
        return True, False
    if os.path.exists(chemin):
        shutil.copy(chemin, chemin + ".avant-chaser-lite-compress.bak")
    h = settings.setdefault("hooks", {})
    h.setdefault("PreToolUse", []).append({
        "matcher": "Bash",
        "hooks": [_entree_hook()]})
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    with open(_manifeste(), "w", encoding="utf-8") as f:
        json.dump({"pose": True}, f)
    return True, True


def retirer():
    if not _charger(_manifeste()):
        return False
    chemin = _settings()
    settings = _charger(chemin)
    if os.path.exists(chemin):
        shutil.copy(chemin, chemin + ".avant-retrait-lite-compress.bak")
    pre = (settings.get("hooks") or {}).get("PreToolUse") or []
    garde = [e for e in pre if "compresseur_lite" not in json.dumps(e)]
    if garde:
        settings["hooks"]["PreToolUse"] = garde
    else:
        settings.get("hooks", {}).pop("PreToolUse", None)
        if not settings.get("hooks"):
            settings.pop("hooks", None)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    os.remove(_manifeste())
    return True


# ----------------------------------------------------------------------------
# 3. Mode HOOK : reçoit le JSON du hook, re-pipe la commande verbeuse
# ----------------------------------------------------------------------------
def mode_hook():
    try:
        j = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    cmd = str((j.get("tool_input") or {}).get("command") or "").strip()
    if not cmd or not VERBEUSES.match(cmd):
        return 0
    if re.search(r"[|;&<>`]|\$\(|compresseur_lite", cmd):
        return 0                                   # commande composée : intacte
    cmd = re.sub(r"^rtk\s+", "", cmd)              # Chaser remplace rtk
    moi = os.path.abspath(__file__).replace("\\", "/")
    nouvelle = f'{cmd} 2>&1 | python "{moi}"; exit ${{PIPESTATUS[0]}}'
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": {**j.get("tool_input", {}), "command": nouvelle}}}))
    return 0


def main():
    argv = sys.argv[1:]
    if "--hook" in argv:
        return mode_hook()
    if "--retirer" in argv:
        ok = retirer()
        print("  Hook de compression retiré. settings.json restauré." if ok
              else "  Rien à retirer.")
        return 0
    if "--appliquer" in argv or "--dry" in argv:
        dispo, applique = appliquer(dry="--appliquer" not in argv)
        print("=" * 56)
        print("  CHASER LITE — Compresseur de sorties (gratuit, réversible)")
        print("=" * 56)
        if not dispo:
            print("  Déjà en place : rien à faire. ✓")
        elif applique:
            print("  Branché. Sauvegarde : settings.json.avant-chaser-lite-compress.bak")
            print("  Redémarre Claude Code. Les grosses sorties (tests, lint, git,")
            print("  find/tree) seront compressées avant d'entrer dans le contexte.")
            print("  Annuler : /chaser-lite:compresser retirer")
        else:
            print("  [DRY] Rien écrit. Relance avec --appliquer.")
        print("\n  Bridé aux familles universelles. CHASER PRO compresse ~60 familles")
        print("  + code (AST) + prose + dédup, avec mesure auditable → "
              "chaser-orchestrator.com/en.html")
        return 0
    # défaut : filtre de flux (stdin -> stdout compressé)
    sys.stdout.write(compresser(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
