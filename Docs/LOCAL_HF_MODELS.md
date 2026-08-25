# Local Hugging Face models

This workspace is prepared for two pinned Hugging Face snapshots:

- `Qwen/Qwen3.8-27B` at `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c`
- `meta-models/Muse-Glimmer-30B` at `a4e59da52a7bc87ae7251dd5545c0dd437c44b68`

The model files are stored outside the source tree under `G:\AI\Models\weights`. The models are multimodal Transformers checkpoints, not Ollama/GGUF models. The local server therefore exposes an OpenAI-compatible API at:

```text
http://127.0.0.1:8000/v1
```

## Pull status

- Qwen is complete at `G:\AI\Models\weights\Qwen3.8-27B-direct` (all 18 weight shards and the index are present; the first shard matches its Hub SHA-256).
- Muse metadata/tokenizer and the first weight shard are present at `G:\AI\Models\weights\Muse-Glimmer-30B-direct`. The first shard is currently a resumable 39 GiB partial transfer; the remaining first-shard range and second shard still need to be downloaded.
- Hugging Face is now authenticated as `Fromage39` (OAuth device flow, token saved to the HF cache). Resume the Muse transfer with `hf download meta-models/Muse-Glimmer-30B --revision a4e59da52a7bc87ae7251dd5545c0dd437c44b68 --local-dir G:\AI\Models\weights\Muse-Glimmer-30B-direct`, or use the memory-efficient Python helper `tools\resume_muse_download.py` (the Rust `hf` CLI can hit a memory-allocation error on the large shards).
- The requested Git pointer clones did not complete; the usable artifacts are the direct snapshot directories above.

## OpenCode

`.opencode.json` contains a non-default `local-hf` provider with these model IDs:

- `local-hf/qwen3.8-27b`
- `local-hf/muse-glimmer-30b`

Start the local server first, then select the model from OpenCode’s model picker. The existing cloud and Ollama providers are intentionally unchanged.

`tools\local_hf_server.py` now enables 4-bit CPU offload (`llm_int8_enable_fp32_cpu_offload=True` plus a `max_memory`/`offload_folder` device map) so the 12 GB GPU can host these models with layers spilled to system RAM. On this workstation the load still fails with `OSError: The paging file is too small (os error 1455)` because the 54 GB Qwen checkpoint cannot be memory-mapped into the current 56 GB pagefile. To run locally, increase the Windows pagefile to ~100 GB (admin + reboot) and retry. Otherwise use a remote/larger-GPU endpoint (see the training note below).

## JCode

Register one profile per model after the local server is running:

```powershell
jcode provider add local-qwen38 --base-url http://127.0.0.1:8000/v1 --model qwen3.8-27b --context-window 262144 --no-api-key --auth none
jcode provider add local-muse-glimmer --base-url http://127.0.0.1:8000/v1 --model muse-glimmer-30b --context-window 131072 --no-api-key --auth none
```

Use `jcode --provider-profile local-qwen38` or `jcode --provider-profile local-muse-glimmer`.

The isolated runtime is `.venv-local-hf`. On this NVIDIA workstation, install the CUDA wheels before the general requirements:

```powershell
uv pip install --python .venv-local-hf\Scripts\python.exe --index-url https://download.pytorch.org/whl/cu128 torch==2.11.0+cu128 torchvision==0.26.0+cu128
uv pip install --python .venv-local-hf\Scripts\python.exe --prerelease=allow -r tools\requirements-local-hf.txt
```

Verify CUDA before loading a model:

```powershell
& .venv-local-hf\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Rider

In Rider, open `Settings | Tools | AI Assistant | Providers & API keys`, choose `OpenAI-compatible`, and set:

- URL: `http://127.0.0.1:8000/v1`
- API key: `local`
- Model: `qwen3.8-27b` or `muse-glimmer-30b`
- Tool calling: enable only after the local server’s tool-call smoke test passes

JetBrains treats local/OpenAI-compatible models separately from the JetBrains AI service. General chat and core features can use these models; inline completion still requires a completion/FIM-capable model.

## Hardware and training note

This workstation has an RTX 4070 SUPER with 12 GB VRAM and 64 GB system RAM (about 30 GB free) with a 56 GB pagefile. The released BF16 checkpoints are suitable for archival/fine-tuning work but do not fit directly in that VRAM budget. Local inference requires a supported 4-bit/CPU-offload path (blocked here by the pagefile limit) or a remote GPU endpoint. No training run is claimed until a runtime loads successfully and a UE/Monolith training corpus and objective are explicitly selected.

The repository includes `tools/build_ue_monolith_corpus.py`, which collects UTF-8 source and documentation records from the active UE/Monolith paths while excluding build products, caches, and credential-like files. It produces raw domain-corpus JSONL, not fabricated instruction/answer pairs. It has been run successfully:

```powershell
& .venv-local-hf\Scripts\python.exe tools\build_ue_monolith_corpus.py `
  --output G:\AI\Models\datasets\ue-monolith-domain.jsonl
```

Result: `G:\AI\Models\datasets\ue-monolith-domain.jsonl` — 2,864 records, ~44.8 MB (1,470 C++, 1,194 Python, 125 Markdown, 46 C#, 17 JSON, and others).

Use that corpus for a separately selected continued-pretraining or LoRA recipe on a larger/remote GPU (e.g. Gradient, Lambda, Vast.ai, or a cloud instance with ≥24 GB VRAM), then validate the resulting adapter against UE C++/Blueprint/Monolith tasks before exposing tool calling.
