# Melodia World-Build Foundation Handoff

## Purpose

This is the next safe production layer while gameplay and portfolio renders are being finalized. The objective is to prepare one authored environment for the JRPG + QuillScript loop without expanding into an open-world build.

## Current authority

- Engine target: UE 5.8.
- Gameplay authority: imported TurnBasedJRPG framework.
- Narrative authority: QuillScript through the project-owned adapter once implemented.
- Presentation authority: Melodia character, environment, lighting, Niagara, and material assets.
- V6 water master: rollback/reference authority; do not edit.
- V7 water master: production candidate with the UE 5.8 Single Layer Water ray-tracing compatibility fix saved and compiling.
- Macro water variation: isolated draft only; it is not yet connected to V7 because the editor function-output wiring rejected the connections.
- Compatibility labs and pre-integration backup remain reference authorities.

## World-build target

Build one contained “quiet-water sanctuary” slice: exploration start, authored dialogue, one allowlisted encounter, battle return, and a visible destination/reward. The environment should support a readable three-minute route and portfolio-quality shots before any larger world expansion.

## Recommended build order

1. **Lock the playable route**
   - Choose one existing sanctuary/WP map.
   - Mark spawn, dialogue point, encounter gate, battle return, reward point, and exit landmark.
   - Keep the route short enough to traverse in under two minutes.

2. **Establish composition before decoration**
   - Create one foreground framing element, one readable midground path, and one background landmark.
   - Reserve a clear battle staging area with camera space and no essential foliage overlap.
   - Place water where it provides visual identity and navigation, not as filler.

3. **Create a world-state layer**
   - Use data-driven IDs for `Spawn`, `Dialogue`, `Encounter`, `Reward`, and `Exit` markers.
   - Keep these markers separate from decorative actors.
   - Do not put gameplay authority in the water material, environment actors, or character presentation Blueprints.

4. **Tune materials after lighting is stable**
   - Validate V7 in the actual level lighting and camera distance.
   - Record material instance overrides rather than changing the master for local art direction.
   - Keep macro breakup, refraction, caustics, and extra layers optional until the base scene is performant.

5. **Add authored atmosphere**
   - Use one ambient audio bed, one encounter cue, restrained particles, and a small number of intentional animated accents.
   - Prefer repeated motifs with controlled variation over uncontrolled procedural density.

6. **Capture and validate**
   - Capture an exploration establishing shot, dialogue composition, battle staging shot, water close-up, and victory-return shot.
   - Test the same route in PIE and Development package.
   - Record frame time, shader warnings, missing assets, and route failures in the session handoff.

## Environment acceptance checklist

- [ ] Player starts at a known named marker.
- [ ] Route to dialogue is visually legible without debug labels.
- [ ] Dialogue point has a clean camera composition and adequate interaction space.
- [ ] Encounter trigger is deterministic and cannot fire twice.
- [ ] Battle staging area has unobstructed character silhouettes and readable ground.
- [ ] Victory, defeat, and flee return to the same safe exploration state.
- [ ] Reward/landmark is visible after return and cannot be granted twice.
- [ ] Water V7 compiles on PCD3D_SM6 in the target map.
- [ ] No production map or asset outside the approved integration namespace is saved accidentally.
- [ ] Scene remains within the agreed performance budget before decorative expansion.

## Do not do yet

- Do not build a second world region.
- Do not add ACFU, Conversation2D, or MelodiaCore runtime authority.
- Do not refactor the water master to solve a local art-direction problem.
- Do not add bespoke quest, inventory, or save logic to environment Blueprints.
- Do not add PCG density until the authored route, battle area, and camera compositions are approved.

## Handoff task for a lower-tier agent

**Task:** Produce an environment-only route brief for the selected sanctuary map.

**Allowed changes:** documentation and non-destructive editor inspection only.

**Required output:** map name, route landmarks, interaction IDs, battle staging constraints, five portfolio camera positions, and a list of missing assets.

**Forbidden:** changing gameplay Blueprints, changing save contracts, editing V6, modifying V7 graph topology, adding plugins, or saving unrelated production assets.

**Completion proof:** attach the route brief and a short risk list; do not claim the gameplay loop passes unless it was actually tested in the editor.

