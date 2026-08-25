CATHEDRAL RIG HANDOFF — v22 ZenRebuild_WIP
============================================

Current State:
- Rig file: Melodia_Portfolio_Stage_v22_ZenRebuild_WIP.blend
- Character rig: 1124 bones
- Melusina.001: 120 shape keys, 52 drivers
- Rig binding: bound to character_rig (armature)
- v43 prep status: driver fix verified 53/53, weight API discovered — proven in old file, in-memory only, nothing on disk changed

v22-Specific Findings:
1. Melusina.001’s two ARMATURE modifiers have obj: None (unbound) — requires fix
2. 52 driver targets need repointing from v43 references to v22 sources
3. Weight audit needed via Object.vertex_groups (Blender 5.2 API)
4. Water-hair + SimplyPin preparation required
5. Review_Queue sync was aborted — needs verification

Fix Sequence (retargeted to v22):
Step 1: Append FaceitControlRig from the rig library into the blend file
Step 2: Repoint all 52 driver targets to v22-appropriate sources (not v43)
Step 3: Rebind the two null ARMature modifiers on Melusina.001 (assign correct armature object)
Step 4: Weight audit — run Object.vertex_groups inspection via Blender 5.2 API
  - Verify all vertex groups are properly assigned
  - Check for unweighted vertices, stray groups, or weight paint issues
Step 5: Water-hair + SimplyPin prep
  - Set up hair particles or groom system
  - Configure SimplyPin constraints for hair locking
Step 6: Verify the aborted Review_Queue sync
  - Check Review_Queue state and restore any pending sync operations
  - Ensure no orphaned data blocks from the aborted session
Step 7: ARP export
  - Export the corrected armature via ARP (Avatar Rig Protocol)
  - Validate the exported rig structure and shape key mapping

Dependencies:
- FaceitControlRig library source
- v22 driver configuration schema
- Blender 5.2 weight painting tools
- SimplyPin plugin/addon
- Review_Queue session state archive
- ARP export pipeline

Next Actions:
1. Open Melodia_Portfolio_Stage_v22_ZenRebuild_WIP.blend in Blender 5.2
2. Execute fix sequence Steps 1-7 in order
3. Verify ARP export validity
4. Update this handoff with completion status and any deviations
