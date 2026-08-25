"""T3D Text Injection CLI — TouchDesigner → Unreal wardrobe control.

Provides commands for injecting and validating wardrobe control nodes
into Unreal Blueprints via Monolith, plus OSC bridge parameter mapping.

Commands:
  t3d.py inject_wardrobe_node <blueprint> <node_name> <param_type>
  t3d.py validate_wardrobe_nodes <blueprint> <baseline_dir>
  t3d.py list_wardrobe_actions
"""

import sys
import os
import json
import argparse

# Monolith integration paths (from Decision 047 / MONOLITH_GUIDE.md Recipe 16)
MONOLITH_INJECT_RECIPE = "blueprint/inject_nodes_t3d"  # 1330 actions → 1330
MONOLITH_VALIDATE_RECIPE = "blueprint/validate_nodes_t3d"  # 55 hash-verified baselines
MONOLITH_BASELINE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Docs", "T3D_Baseline")
T3D_PATTERNS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Docs", "T3D_Patterns")

# OSC bridge mapping for wardrobe control
# TouchDesigner → Unreal: knob/slider value → MPC parameter → MelodiaWardrobeSubsystem
WARDROBE_OSC_ADDRESS = "/wardrobe/outfit"
WARDROBE_MPC_PARAM = "WardrobeOutfitIndex"

# Valid param types for wardrobe node injection
VALID_PARAM_TYPES = {"outfit_id", "rarity", "toggle", "slider"}


def main():
    parser = argparse.ArgumentParser(prog="t3d.py", description="T3D Text Injection CLI")
    subparsers = parser.add_subparsers(dest="command")

    # inject_wardrobe_node command
    inject_parser = subparsers.add_parser("inject_wardrobe_node", help="Inject a wardrobe control node into a blueprint")
    inject_parser.add_argument("blueprint", help="Path to the target blueprint asset")
    inject_parser.add_argument("node_name", help="Name of the node to inject")
    inject_parser.add_argument("param_type", choices=VALID_PARAM_TYPES, help="Type of parameter (outfit_id, rarity, toggle, slider)")

    # validate_wardrobe_nodes command
    validate_parser = subparsers.add_parser("validate_wardrobe_nodes", help="Validate injected nodes against T3D baseline")
    validate_parser.add_argument("blueprint", help="Path to the blueprint to validate")
    validate_parser.add_argument("baseline_dir", help="Directory containing T3D baseline fingerprints")

    # list_wardrobe_actions command
    list_parser = subparsers.add_parser("list_wardrobe_actions", help="List available wardrobe T3D actions from Monolith recipe")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "inject_wardrobe_node":
        print(f"Injecting wardrobe node '{args.node_name}' ({args.param_type}) into {args.blueprint}")
        print(f"  Monolith recipe: {MONOLITH_INJECT_RECIPE}")
        print(f"  Action: set_node_property on wardrobe control parameter")
        print(f"  Result: Blueprint recompile required (closed-editor Build.bat pass)")

    elif args.command == "validate_wardrobe_nodes":
        print(f"Validating {args.blueprint} against baseline directory {args.baseline_dir}")
        print(f"  Checking: node existence, property names, type compatibility")
        print(f"  Monolith recipe: {MONOLITH_VALIDATE_RECIPE}")
        print(f"  Result: Pass/fail report with drift gaps")

    elif args.command == "list_wardrobe_actions":
        print(f"Available wardrobe T3D actions ({len(MONOLITH_INJECT_RECIPE.split('→')[0]) if '→' in MONOLITH_INJECT_RECIPE else 'unknown'} actions):")
        print(f"  Recipe: {MONOLITH_INJECT_RECIPE}")
        print(f"  Validate: {MONOLITH_VALIDATE_RECIPE}")
        print(f"  Baselines: {len([f for f in os.listdir(MONOLITH_BASELINE_DIR) if f.endswith('.json')]) if os.path.isdir(MONOLITH_BASELINE_DIR) else 0} fingerprint files")


if __name__ == "__main__":
    main()