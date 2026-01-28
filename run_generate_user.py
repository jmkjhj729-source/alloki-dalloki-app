#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_generate_user.py
Safe wrapper around run_generate.py.
- Reads user assets dir from --assets_dir (wrapper-only) and exposes it as env vars.
- Collects wrapper-only outputs: zip_out, preview_html, hook_tone, cta_tone.
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    env = dict(os.environ)

    def pop_arg(flag, takes_value=True):
        nonlocal argv
        if flag in argv:
            i = argv.index(flag)
            if takes_value and i+1 < len(argv) and not argv[i+1].startswith("--"):
                val = argv[i+1]
                argv = argv[:i] + argv[i+2:]
                return val
            argv = argv[:i] + argv[i+1:]
            return "1"
        return None

    assets_dir = pop_arg("--assets_dir", True)
    user_edit = pop_arg("--user_edit", True)
    zip_out = pop_arg("--zip_out", True)
    preview_html = pop_arg("--preview_html", True)
    hook_tone = pop_arg("--hook_tone", True)
    cta_tone = pop_arg("--cta_tone", True)

    if assets_dir:
        env["ALLOKI_ASSETS_DIR"] = str(Path(assets_dir).resolve())
    if user_edit:
        env["ALLOKI_USER_EDIT"] = str(user_edit)
    if zip_out:
        env["ALLOKI_ZIP_OUT"] = str(Path(zip_out).resolve())
    if preview_html:
        env["ALLOKI_PREVIEW_HTML"] = str(Path(preview_html).resolve())
    if hook_tone:
        env["ALLOKI_HOOK_TONE"] = str(hook_tone)
    if cta_tone:
        env["ALLOKI_CTA_TONE"] = str(cta_tone)

    cmd = [sys.executable, str(ROOT/"run_generate.py")] + argv
    p = subprocess.run(cmd, cwd=str(ROOT), env=env)
    return int(p.returncode)

if __name__ == "__main__":
    raise SystemExit(main())
