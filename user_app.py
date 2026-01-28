#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alloki & Dalloki USER Edition
GUI: streamlit run ui_streamlit.py
CLI: python user_app.py generate_week --season spring --platforms instagram,tiktok --segments new,repeat
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent

def _run(cmd: List[str]) -> int:
    p = subprocess.run(cmd, cwd=str(ROOT))
    return int(p.returncode)

def cmd_generate_week(args) -> int:
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    segments  = [s.strip() for s in args.segments.split(",") if s.strip()]
    out_root = Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    forward = args.forward_args or []
    rc = 0
    for plat in platforms:
        for seg in segments:
            out_dir = out_root / f"{args.season}" / plat / seg
            out_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable, str(ROOT/"run_generate_user.py"),
                "--season", args.season,
                "--platform", plat,
                "--segment", seg,
                "--days", str(args.days),
                "--format", args.format,
                "--mode", args.mode,
                "--offer_code", args.offer_code,
                "--assets_dir", str(Path(args.assets_dir)),
                "--message_out", str(out_dir/"message_payload.json"),
                "--log_xlsx", str(Path(args.log_xlsx)),
                "--platform_ev_config", str(Path(args.platform_ev_config)),
                "--user_edit", "1",
            ]

            if not args.no_zip:
                cmd += ["--zip_out", str(out_dir/"package.zip")]
            if args.preview_html:
                cmd += ["--preview_html", str(out_dir/"preview.html")]
            if args.dry_run:
                cmd += ["--dry_run"]

            cmd += forward
            print("\n[RUN]", " ".join(cmd))
            rc = _run(cmd)
            if rc != 0:
                return rc
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Alloki & Dalloki USER Edition (safe distribution)")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate_week", help="Generate weekly sets (platform x segment). No upload/send by default.")
    g.add_argument("--season", required=True, help="spring/summer/autumn/winter/yearend OR promo labels like promo_d-3")
    g.add_argument("--platforms", default="instagram,tiktok")
    g.add_argument("--segments", default="new,repeat")
    g.add_argument("--days", type=int, default=7)
    g.add_argument("--offer_code", default="D7")
    g.add_argument("--format", default="both", help="square|story|both")
    g.add_argument("--mode", default="paid", help="paid/free-lock etc (depends on generator)")
    g.add_argument("--assets_dir", default="./user_assets", help="where user puts PNGs/backgrounds")
    g.add_argument("--out_dir", default="./out_user")
    g.add_argument("--log_xlsx", default="./performance_log.xlsx")
    g.add_argument("--platform_ev_config", default="./platform_ev_config.json")
    g.add_argument("--no_zip", action="store_true")
    g.add_argument("--preview_html", action="store_true")
    g.add_argument("--dry_run", action="store_true")
    g.add_argument("forward_args", nargs=argparse.REMAINDER, help="extra args forwarded to generator")
    g.set_defaults(func=cmd_generate_week)

    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
