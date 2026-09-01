#!/usr/bin/env python
"""DEPRECATED — use toolchain/ue/oneclick_seaabove.py instead.

That script is the maintained one-click path (VDB import -> volume material ->
Niagara system skeleton) and uses real UE 5.8 Python APIs. This file previously
used fabricated API calls (set_material / add_emitter_instance) and cannot run.
Kept only as a pointer so old references don't 404.
"""


def create_niagara_system(*_a, **_k):
    raise NotImplementedError(
        "Use toolchain/ue/oneclick_seaabove.py (import oneclick_seaabove; "
        "oneclick_seaabove.run())")


create_volume_material = create_niagara_system

