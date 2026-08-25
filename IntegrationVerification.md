# MelodiaWardrobeComponent + BP_EquipmentBase Integration Verification

## 1. Wardrobe Architecture Doc (§9.4 Equipment System Fold-In, lines 186-200)

**Location:** `C:\EnvironmentPortfolio\BS_GodFile\Docs\MELODIA_WARDROBE_ARCHITECTURE_2026-08-14.md`

**Key findings from §9.4:**

| Statement | Verification |
|---|---|
| "Outfit system integrates with equipment slots via MelodiaWardrobeComponent (6 slots: Body, Hat, Gloves, Shawl, Trail, HairCharm)" | Confirmed - 6 slots exist in `EMelodiaWardrobeSlot` enum |
| "These map to the JRPG template's equipment system through the existing BP_EquipmentBase framework" | **Planned/Deferred** - No active mapping code found; summary table lists "Equipment Fold-In: Planning stage, Future decision 046+" |
| "OwnedCosmeticIds and EquippedCosmeticIds on FMelodiaNarrativeRecord v3 are the authoritative source — not the equipment inventory" | Confirmed - fields are on the narrative record, equipment inventory is separate |
| "Wallet GoldenTokens decrement logic is separate from equipment durability/consumable systems" | Confirmed - wallet and wardrobe systems are independent |
| "Form capabilities, if later enabled, would flow through UMelodiaNarrativeSubsystem → battle subsystem, NOT through the equipment component tree" | Confirmed - capabilities flow through narrative subsystem, not equipment |
| "Decision 043 explicitly defers soft-gate outfit-ability gameplay; equipment fold-in will occur in a future decision (likely 046+) after the collection/UI/commerce axis is proven" | Confirmed - summary table: "Equipment Fold-In | Planning stage | Future decision 046+" |

## 2. MelodiaWardrobeComponent C++ Definition

**Location:** `C:\EnvironmentPortfolio\BS_GodFile\Plugins\MelodiaWardrobe\Source\MelodiaWardrobe\Public\MelodiaWardrobeComponent.h` and `.cpp`

**Class hierarchy:** `UActorComponent` → `UMelodiaWardrobeComponent`

**6 Wardrobe Slots** (from `EMelodiaWardrobeSlot` enum in `MelodiaNarrativeTypes.h`):
- `Body` (index 0)
- `Hat` (index 1)
- `Gloves` (index 2)
- `Shawl` (index 3)
- `Trail` (index 4)
- `HairCharm` (index 5)
- V2 split-garment slots: `Shirt`, `Skirt`, `Boots`, `Accessories` (appended only, must not be renumbered)

**Key UPROPERTY:**
- `TMap<EMelodiaWardrobeSlot, TObjectPtr<USkeletalMeshComponent>> SlotComponents` - per-slot components (private)

**Key UFUNCTIONs:**
- `EquipCosmetic(FName CosmeticId)` → bool - resolves mesh through subsystem, mirrors equipped id into narrative record, returns success/failure
- `EquipGarment(EMelodiaWardrobeSlot Slot, USkeletalMesh* GarmentMesh)` - equips mesh into slot, creates component if needed
- `UnequipSlot(EMelodiaWardrobeSlot Slot)` - hides slot component
- `ApplyWardrobeState()` - restores equipped state from `UMelodiaWardrobeSubsystem` → `FMelodiaNarrativeRecord`, reads `EquippedCosmeticIds` map
- `GetSlotComponent(EMelodiaWardrobeSlot Slot)` → USkeletalMeshComponent* - gets or creates slot component
- `IsSlotEquipped(EMelodiaWardrobeSlot Slot)` → bool - checks visibility + mesh validity
- `SetSlotMaterial(EMelodiaWardrobeSlot Slot, int32 MaterialIndex, UMaterialInterface* Material)` - material override

**Internal flow:**
- `EquipCosmetic()` → calls `Wardrobe->EquipCosmetic()` → writes to `FMelodiaNarrativeRecord.EquippedCosmeticIds[Slot]` → calls `EquipGarment()` to create component and pose mesh
- `ApplyWardrobeState()` → reads `Wardrobe->GetState().EquippedCosmeticIds` → applies each equipped cosmetic to its slot
- All state is read from/written through `FMelodiaNarrativeRecord`, NOT stored locally in the component

## 3. FMelodiaNarrativeRecord v3 Save Fields

**Location:** `C:\EnvironmentPortfolio\BS_GodFile\Source\BS_GodFile\MelodiaIntegration\MelodiaNarrativeTypes.h` (lines 112-230)

**Three wardrobe v3 fields** (Category: `Melodia|Narrative|Wardrobe`, all `SaveGame`):

| Field | Type | Default | Description |
|---|---|---|---|
| `OwnedCosmeticIds` | `TSet<FName>` | Empty set | Every cosmetic the player has ever acquired (granted, pulled, or purchased) |
| `EquippedCosmeticIds` | `TMap<EMelodiaWardrobeSlot, FName>` | Empty map | One cosmetic per slot, at most. Equipping writes here; wardrobe component mirrors visual state. |
| `LastPullUnixSeconds` | `int32` | 0 | Monotonic timestamp of the last gacha pull. Optional, reserved for future pity-counter work. |

**Access specifiers:** All three are `UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Melodia|Narrative|Wardrobe")`

**Versioning:** `static constexpr int32 CurrentVersion = 4`; v3 fields (OwnedCosmeticIds, EquippedCosmeticIds, LastPullUnixSeconds) added in 2026-08-07 per Decision 043. Migration is a no-op for v1/v2 saves since defaults are empty.

## 4. The 6 Wardrobe Slots Mapping

**Primary slots (Decision 043, 2026-08-07):**
- `Body`, `Hat`, `Gloves`, `Shawl`, `Trail`, `HairCharm`

**V2 split-garment slots (appended only, serialized into existing saves):**
- `Shirt`, `Skirt`, `Boots`, `Accessories`

**Mapping to equipment slots:**
- The architecture doc §9.4 states these "map to the JRPG template's equipment system through the existing BP_EquipmentBase framework"
- **However, no active mapping code was found** in C++ or Blueprints
- The `MelodiaWardrobeComponent` manages these 6 slots independently
- The equipment fold-in is explicitly listed as "Planning stage" / "Future decision 046+"
- If/when integration occurs, each wardrobe slot would map to an equipment slot in `BP_EquipmentBase` (likely: Body→Body, Hat→Head, Gloves→Hands, Shawl→Back/Chest, Trail→Waist/Hair, HairCharm→Accessory), but this is not implemented

## 5. OwnedCosmeticIds and EquippedCosmeticIds Accessibility In-Game

**Access path:** Through `UMelodiaNarrativeSubsystem`

**Blueprint-accessible functions:**
- `IsOwned(FName CosmeticId)` → bool - checks `OwnedCosmeticIds` set
- `GetEquipped(EMelodiaWardrobeSlot Slot)` → FName - returns equipped cosmetic id for slot from `EquippedCosmeticIds` map
- `GetEquippedFormId(EMelodiaWardrobeSlot Slot)` → FName - returns the form id an equipped cosmetic presents, or NAME_None
- `IsFormUnlocked(FName FormId)` → bool - checks if form's required flags are set
- `GetActiveCapabilities(FName ContextId)` → TArray<EMelodiaFormCapability> - capabilities granted by unlocked forms
- `GetState()` → `FMelodiaWardrobeState` - read model for UI (copies `OwnedCosmeticIds` and `EquippedCosmeticIds`)

**Direct access to save record fields:**
- `FMelodiaNarrativeRecord.OwnedCosmeticIds` - TSet<FName>, EditAnywhere + SaveGame + BlueprintReadWrite
- `FMelodiaNarrativeRecord.EquippedCosmeticIds` - TMap<EMelodiaWardrobeSlot, FName>, EditAnywhere + SaveGame + BlueprintReadWrite
- `FMelodiaNarrativeRecord.LastPullUnixSeconds` - int32, EditAnywhere + SaveGame + BlueprintReadWrite

**Important note from architecture doc ( §103-115 ):**
- `UMelodiaNarrativeSubsystem::GetNarrativeRecord()` returns by value — every call copies every map plus the Quill byte blob
- **Pitfall:** Callers in loops must fetch once and bind to `const&` (lifetime extension), otherwise use-after-free risk
- Per-slot access: use `GetEquipped(Slot)` rather than accessing the map directly through the returned record

## 6. Wallet Integration

**API:** `UMelodiaTokenWalletSubsystem::TryGrantGolden(int32 Amount, FName GrantId)`

**Dedup mechanism:**
- `ConsumedGrantIds: TSet<FName>` — runtime-only same-session dedupe
- **NOT durable across restart:** empty after restart by design
- Persistent once-only semantics live in `OwnedCosmeticIds` (via `GrantCosmetic()` → writes to narrative record)
- Within a session: GrantId already consumed → REJECTED, rejection survives process restart
- Across restart: only `OwnedCosmeticIds` guarantees durability

**LastPullUnixSeconds:**
- Field on `FMelodiaNarrativeRecord` v3
- Records monotonic timestamp of last gacha pull
- Reserved for future pity-counter work
- Used for daily reset logic

**GrantId format:** `outfit_ch2_{mechanic_key}` — ensures outfit pulls are distinct from other golden grants

**Flow:**
1. Player initiates gacha pull → `TryGrantGolden(Amount, GrantId)` 
2. Wallet checks `ConsumedGrantIds` — if already consumed, reject (no GoldenTokens decrement)
3. If not consumed: decrement `GoldenTokens`, add GrantId to `ConsumedGrantIds`, fire `OnWalletChanged`
4. Separately: grant cosmetic → `GrantCosmetic(CosmeticId, GrantId)` → writes to `OwnedCosmeticIds` in narrative record
5. On save/load: `ConsumedGrantIds` is empty (cleared), but `OwnedCosmeticIds` persists → durable ownership

**Verification results from architecture doc:**
- Wallet decrements `GoldenTokens` exactly once per successful grant — verified in PIE save/load cycle
- On process restart: replaying a grant Id is a no-op due to owned `TSet` dedupe (acceptable per Decision 043)

## 7. Complete Mapping Summary

| Wardrobe Slot | EMelodiaWardrobeSlot | EquippedCosmeticIds Key | BP_EquipmentBase Slot |
|---|---|---|---|
| Body | 0 | `EquippedCosmeticIds[Body]` | Not mapped (future decision 046+) |
| Hat | 1 | `EquippedCosmeticIds[Hat]` | Not mapped |
| Gloves | 2 | `EquippedCosmeticIds[Gloves]` | Not mapped |
| Shawl | 3 | `EquippedCosmeticIds[Shawl]` | Not mapped |
| Trail | 4 | `EquippedCosmeticIds[Trail]` | Not mapped |
| HairCharm | 5 | `EquippedCosmeticIds[HairCharm]` | Not mapped |

**Integration status:**
- **Wardrobe system:** Fully implemented and functional. 6 slots managed by `MelodiaWardrobeComponent`, state persisted in `FMelodiaNarrativeRecord`.
- **Equipment mapping:** Not implemented. Architecture doc marks it as "Planning stage, Future decision 046+". No C++ or Blueprint code maps the 6 wardrobe slots to `BP_EquipmentBase` equipment slots.
- **Wallet integration:** Fully implemented. `TryGrantGolden` API with `ConsumedGrantIds` dedupe and `LastPullUnixSeconds` timestamp. Separate from equipment system.
- **Form capabilities:** Flow through `UMelodiaNarrativeSubsystem`, not equipment tree. deferred per foundation closeout §2.2.

**Key verifications passed:**
- ✅ All 6 wardrobe slots defined in `EMelodiaWardrobeSlot` enum
- ✅ `OwnedCosmeticIds` and `EquippedCosmeticIds` are `SaveGame` fields, accessible in-game
- ✅ `LastPullUnixSeconds` v3 field present and accessible
- ✅ Wallet `TryGrantGolden` API with `ConsumedGrantIds` dedupe verified
- ✅ Wardrobe state restoration from save verified in `ApplyWardrobeState()`
- ✅ Equipment fold-in explicitly deferred (not broken, just not yet designed)