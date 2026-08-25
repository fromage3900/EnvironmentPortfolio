#!/usr/bin/env python3
"""
One-shot Figma sync script for CI / manual runs.

Usage:
    FIGMA_TOKEN=xxx python tools/figma_sync.py [--dry-run] [--kit] [--motion]

Exports:
- SoftMG Kit + Filigree Baroque -> generated/assets/melodia-game-ui/
- Updates ART_SOURCE.json
- Updates wix/melodia-motion-connect.json
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent))

from figma_mcp import FigmaClient, NODE_MAP, FILE_KEY, EXPORT_SCALE, EXPORT_FORMAT


async def export_node_images(client: FigmaClient, node_ids: list, dest: Path) -> dict:
    """Export PNGs for node IDs."""
    dest.mkdir(parents=True, exist_ok=True)

    img_data = await client.get_image_urls(FILE_KEY, node_ids, EXPORT_SCALE, EXPORT_FORMAT)
    images = img_data.get("images", {})

    mapping = {}
    for node_id, url in images.items():
        if not url:
            print(f"  ⚠ No export URL for {node_id}", file=sys.stderr)
            continue

        safe_id = node_id.replace(":", "_")
        ext = f".{EXPORT_FORMAT}"
        filename = f"T_Melodia_{safe_id}{ext}"
        filepath = dest / filename

        content = await client.download_image(url)
        filepath.write_bytes(content)
        mapping[node_id] = filename
        print(f"  ✓ {node_id} -> {filename}")

    return mapping


async def find_child_ids(client: FigmaClient, parent_node_id: str, expected_names: list) -> list:
    """Find child node IDs by name under a parent frame."""
    nodes_data = await client.get_file_nodes(FILE_KEY, [parent_node_id])
    parent = nodes_data["nodes"][parent_node_id]["document"]

    found = []

    def search(node):
        if isinstance(node, dict):
            name = node.get("name", "")
            if name in expected_names and "id" in node:
                found.append(node["id"])
            for child in node.get("children", []):
                search(child)

    search(parent)
    return found


async def sync_kit(client: FigmaClient, dest: Path, dry_run: bool = False) -> dict:
    """Sync SoftMG Kit + Filigree Baroque."""
    print("[ART] Syncing SoftMG Kit + Filigree Baroque...")

    # SoftMG Kit children
    softmg_names = [
        "SoftMG/ParchmentPanel",
        "SoftMG/ScrollEdge",
        "SoftMG/SealSP",
        "SoftMG/SealULT",
        "SoftMG/LaneInk",
        "SoftMG/Hitline",
        "SoftMG/PillowChip",
    ]
    softmg_ids = await find_child_ids(client, NODE_MAP["softmg_kit"], softmg_names)
    print(f"  Found {len(softmg_ids)}/{len(softmg_names)} SoftMG nodes")

    # Filigree Baroque children (Figma node names use "style=" prefix)
    baroque_names = [
        "FiligreeBatchO_Baroque",
        "style=CornerBaroque",
        "style=DividerScroll",
        "style=CrestBaroque",
        "style=MedallionRosette",
        "style=BraceVolute",
    ]
    baroque_ids = await find_child_ids(client, NODE_MAP["filigree_baroque"], baroque_names)
    print(f"  Found {len(baroque_ids)}/{len(baroque_names)} Baroque nodes")

    all_ids = softmg_ids + baroque_ids

    if dry_run:
        print("  [DRY RUN] Would export:", all_ids)
        return {}

    mapping = await export_node_images(client, all_ids, dest)

    return {
        "softmg_nikki_fab_pass": {
            "figma_status": "exported",
            "exported_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "slots": [mapping.get(nid, f"MISSING_{nid}") for nid in softmg_ids],
            "figma_nodes": dict(zip(softmg_names, softmg_ids)),
        },
        "baroque_slots": [mapping.get(nid, f"MISSING_{nid}") for nid in baroque_ids],
        "figma_nodes": dict(zip(baroque_names, baroque_ids)),
    }


async def sync_motion(client: FigmaClient, dest: Path, dry_run: bool = False) -> dict:
    """Sync motion board (RhythmReactivityBoard)."""
    print("[MOTION] Syncing Motion Board...")

    motion_nodes = {
        "95:1857": "Motion/StaffShimmer",
        "95:1858": "Motion/NoteTrailIri",
        "95:1859": "Motion/BreakCrestReveal",
        "41:249": "Motion/FiligreeBreathe",
        "41:287": "Motion/DividerScroll",
        "41:313": "Motion/BraceVolute",
        "41:341": "Motion/GradeHalo/Perfect",
        "41:354": "Motion/GradePopLuxury",
        "41:357": "Motion/StreakGlowEdge",
        "41:362": "Motion/CrestBaroque",
        "41:380": "Motion/HitlinePulse",
        "41:381": "Motion/PhaseDim",
        "41:386": "Motion/ULTArcPulse",
        "41:388": "Motion/SPMeterShimmer",
        "41:390": "Motion/MobileLanePress",
        "58:721": "Motion/PortraitIri",
        "58:760": "Motion/BaroqueMedallion",
        "58:783": "Motion/BraceVoluteSheen",
    }

    # Get board node to find which motion nodes exist
    nodes_data = await client.get_file_nodes(FILE_KEY, [NODE_MAP["motion_board"]])
    board = nodes_data["nodes"][NODE_MAP["motion_board"]]["document"]

    found = []

    def search(node):
        if isinstance(node, dict):
            nid = node.get("id")
            if nid in motion_nodes:
                found.append(nid)
            for child in node.get("children", []):
                search(child)

    search(board)
    print(f"  Found {len(found)}/{len(motion_nodes)} motion nodes")

    if dry_run:
        print("  [DRY RUN] Would export:", found)
        return {}

    mapping = await export_node_images(client, found, dest)

    # Read existing manifest
    manifest_path = Path("wix/melodia-motion-connect.json")
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    manifest.setdefault("motion_connect_pass", {})["last_export"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    manifest["motion_connect_pass"]["figma_export_status"] = "exported"
    manifest["motion_connect_pass"]["exported_nodes"] = {nid: mapping.get(nid) for nid in found}

    return {"motion_connect": manifest}


async def main():
    parser = argparse.ArgumentParser(description="Figma one-shot sync for Melodia")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files, just show what would be done")
    parser.add_argument("--kit", action="store_true", help="Sync only SoftMG/Baroque kit")
    parser.add_argument("--motion", action="store_true", help="Sync only motion board")
    parser.add_argument("--chrome", action="store_true", help="Also regenerate Blender chrome PNGs from wix/melodia-tokens.css (gold-ivory/pink) -> melodia_chrome/")
    parser.add_argument("--dest", default="generated/assets/melodia-game-ui", help="Export destination")
    args = parser.parse_args()

    # Chrome regen is local-only (tokens.css -> PNG) and does NOT need FIGMA_TOKEN
    if args.chrome:
        try:
            import subprocess, pathlib as _pl
            chrome_script = _pl.Path(__file__).parent / "generate_chrome_icons.py"
            if chrome_script.exists():
                print("[CHROME] Regenerating gold-ivory/pink header & preset cards...")
                if args.dry_run:
                    print(f"  [DRY RUN] would run {chrome_script}")
                else:
                    res = subprocess.run([sys.executable, str(chrome_script)], capture_output=True, text=True)
                    print(res.stdout)
                    if res.stderr:
                        print(res.stderr, file=sys.stderr)
                    triage = _pl.Path(__file__).parent / "audit_gn_builders.py"
                    if triage.exists():
                        subprocess.run([sys.executable, str(triage)], capture_output=True)
                print("  ✓ Chrome regenerated")
                if not os.getenv("FIGMA_TOKEN") and not (args.kit or args.motion):
                    print("\n✅ Chrome-only sync complete (no FIGMA_TOKEN needed)")
                    return 0
        except Exception as exc:
            print(f"  ⚠ Chrome regen failed: {exc}", file=sys.stderr)
        # if chrome + kit/motion and no token, fall through to token error intentionally

    if not os.getenv("FIGMA_TOKEN"):
        # If --chrome was the only request and we already returned, we never get here.
        # Otherwise, kit/motion needs token.
        print("ERROR: FIGMA_TOKEN env var required (use --chrome for local-only chrome regen)", file=sys.stderr)
        sys.exit(1)

    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    async with FigmaClient() as client:
        results = {}

        if args.kit or not (args.motion):
            results.update(await sync_kit(client, dest, args.dry_run))

        if args.motion or not (args.kit):
            motion_result = await sync_motion(client, dest, args.dry_run)
            if motion_result.get("motion_connect"):
                # Write motion manifest immediately
                if not args.dry_run:
                    manifest_path = Path("wix/melodia-motion-connect.json")
                    manifest_path.write_text(json.dumps(motion_result["motion_connect"], indent=2))
                    print(f"  ✓ Updated {manifest_path}")

        # Update ART_SOURCE.json
        if not args.dry_run:
            art_source_path = dest / "ART_SOURCE.json"
            if art_source_path.exists():
                art = json.loads(art_source_path.read_text())
            else:
                art = {}

            art.update(results)
            art["last_full_export"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
            art_source_path.write_text(json.dumps(art, indent=2))
            print(f"  ✓ Updated {art_source_path}")

        # Autosync chrome after any kit/motion export so preset cards + rules stay in sync with tokens
        if not args.dry_run:
            try:
                import subprocess, pathlib as _pl
                chrome_script = _pl.Path(__file__).parent / "generate_chrome_icons.py"
                if chrome_script.exists():
                    print("[CHROME] Post-sync regeneration...")
                    subprocess.run([sys.executable, str(chrome_script)], capture_output=True)
            except Exception:
                pass

    print("\n✅ Sync complete")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))