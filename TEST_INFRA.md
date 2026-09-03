# E2E Test Infra: Texture Catalog Dashboard

## Test Philosophy
- Opaque-box, requirement-driven testing. No dependency on implementation design.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial Testing + Real-World Workload Testing.

## Feature Inventory
| # | Feature | Source (Requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Data Mapping Count (>=1500) | ORIGINAL_REQUEST Criteria 1 | 5 | 5 | ✓ |
| 2 | File Existence on Disk | ORIGINAL_REQUEST Criteria 1 | 5 | 5 | ✓ |
| 3 | PBR Map Type Categorization | ORIGINAL_REQUEST R1 | 5 | 5 | ✓ |
| 4 | Usage Context Assignment | ORIGINAL_REQUEST R1 | 5 | 5 | ✓ |
| 5 | DOM Shell & Semantic Layout | ORIGINAL_REQUEST R2 | 5 | 5 | ✓ |
| 6 | Search Input & Substring Match | ORIGINAL_REQUEST R2 | 5 | 5 | ✓ |
| 7 | Channel Filter Isolation | ORIGINAL_REQUEST R2 & Criteria 2 | 5 | 5 | ✓ |
| 8 | Thumbnail Image References | ORIGINAL_REQUEST R2 | 5 | 5 | ✓ |
| 9 | Standalone Zero-Dependency Execution | ORIGINAL_REQUEST R2 | 5 | 5 | ✓ |
| 10 | Zero-Slop & Content Hygiene | Workspace Rules | 5 | 5 | ✓ |

## Test Architecture
- Test Runner: `pytest` executing `tests/test_texture_catalog_dashboard.py`
- Test Harness: `wix/tests/dom_harness.py` for HTML5 DOM parsing and CSS AST inspection
- Data Verification: Programmatic assertions against `catalog-data.json` and disk files

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Complete Catalog Integrity Audit | F1, F2, F3, F4 (1500+ textures with valid paths on disk) | High |
| 2 | PBR Channel Filter Precision (All 10 Channels) | F3, F7 (Querying each channel returns 100% matching items) | High |
| 3 | Multi-term Search & Case-Insensitive Matching | F6, F7 (Search across names, families, contexts) | Medium |
| 4 | Offline Standalone HTML DOM & Asset Binding | F5, F8, F9 (Complete DOM parse without network/runtime errors) | Medium |
| 5 | Content Hygiene & Zero Leaked Tokens | F10 (Zero debug markers, ports, or raw pointers) | Low |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature (where boundaries exist)
- Tier 3: Pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
