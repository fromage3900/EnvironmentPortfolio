"""Small localhost-only OpenAI-compatible server for the pinned HF checkpoints."""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field


MODEL_DEFAULTS = {
    "qwen3.8-27b": {
        "path_env": "LOCAL_HF_QWEN_PATH",
        "default_path": r"G:\AI\Models\weights\Qwen3.8-27B-direct",
        "context": 262_144,
    },
    "muse-glimmer-30b": {
        "path_env": "LOCAL_HF_MUSE_PATH",
        "default_path": r"G:\AI\Models\weights\Muse-Glimmer-30B-direct",
        "context": 131_072,
    },
}


class ChatRequest(BaseModel):
    model: str
    messages: list[dict[str, Any]]
    max_tokens: int | None = Field(default=1024, ge=1, le=32_768)
    temperature: float | None = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float | None = Field(default=0.95, gt=0.0, le=1.0)
    stream: bool = False
    tools: list[dict[str, Any]] | None = None
    tool_choice: Any | None = None


class LocalHFServer:
    def __init__(self, model_id: str, precision: str) -> None:
        if model_id not in MODEL_DEFAULTS:
            raise ValueError(f"Unsupported model: {model_id}")
        self.model_id = model_id
        self.precision = precision
        config = MODEL_DEFAULTS[model_id]
        self.model_path = Path(os.getenv(config["path_env"], config["default_path"]))
        self.processor = None
        self.model = None
        self.torch = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise RuntimeError(f"Model path does not exist: {self.model_path}")

        try:
            import torch
            import transformers
        except ImportError as exc:
            raise RuntimeError(
                "Local HF runtime dependencies are missing. Install "
                "tools/requirements-local-hf.txt first."
            ) from exc

        self.torch = torch
        try:
            from transformers import AutoModelForImageTextToText, AutoProcessor
        except ImportError as exc:
            raise RuntimeError(
                "This checkpoint needs a recent Transformers build with "
                "AutoModelForImageTextToText support."
            ) from exc

        quantization_config = None
        if self.precision == "4bit":
            try:
                from transformers import BitsAndBytesConfig

                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    # Allow modules that do not fit in GPU VRAM to be
                    # dispatched to CPU/disk instead of erroring out.
                    llm_int8_enable_fp32_cpu_offload=True,
                )
            except ImportError as exc:
                raise RuntimeError(
                    "4-bit mode requires the bitsandbytes extra. "
                    "Use --precision bf16 only on hardware with enough memory."
                ) from exc

        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            trust_remote_code=True,
        )
        load_kwargs: dict[str, Any] = {
            "trust_remote_code": True,
            "device_map": "auto",
            "torch_dtype": "auto",
            "low_cpu_mem_usage": True,
        }
        if quantization_config is not None:
            load_kwargs["quantization_config"] = quantization_config
            # Reserve ~10 GiB for the GPU and let the rest spill to CPU RAM.
            # This is required for the 12 GB RTX 4070 SUPER to host these
            # 27B/30B models in 4-bit with CPU offload.
            load_kwargs["max_memory"] = {0: "10GiB", "cpu": "48GiB"}
            load_kwargs["offload_folder"] = str(
                self.model_path.parent / f"{self.model_id}-offload"
            )
            load_kwargs["offload_state_dict"] = True

        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            **load_kwargs,
        )
        self.model.eval()

    def _prepare_inputs(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
    ) -> Any:
        if self.processor is None or self.model is None:
            raise RuntimeError("Model is not loaded")

        template_kwargs: dict[str, Any] = {
            "add_generation_prompt": True,
            "tokenize": True,
            "return_dict": True,
            "return_tensors": "pt",
        }
        if tools:
            template_kwargs["tools"] = tools
        try:
            inputs = self.processor.apply_chat_template(messages, **template_kwargs)
        except TypeError:
            template_kwargs.pop("tools", None)
            inputs = self.processor.apply_chat_template(messages, **template_kwargs)

        device = getattr(self.model, "device", None)
        if device is not None:
            for key, value in inputs.items():
                if hasattr(value, "to"):
                    inputs[key] = value.to(device)
        return inputs

    def generate(self, request: ChatRequest) -> str:
        inputs = self._prepare_inputs(request.messages, request.tools)
        generation: dict[str, Any] = {
            "max_new_tokens": request.max_tokens or 1024,
            "top_p": request.top_p or 0.95,
            "use_cache": True,
        }
        if request.temperature is not None and request.temperature > 0:
            generation.update({"do_sample": True, "temperature": request.temperature})
        else:
            generation["do_sample"] = False

        with self.torch.inference_mode():
            output_ids = self.model.generate(**inputs, **generation)

        input_ids = inputs.get("input_ids")
        if input_ids is not None:
            output_ids = output_ids[:, input_ids.shape[-1] :]
        return self.processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()


def completion_payload(model_id: str, content: str, prompt_tokens: int = 0) -> dict[str, Any]:
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    completion_tokens = max(1, len(content.split()))
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_id,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def stream_payload(model_id: str, content: str) -> Iterator[str]:
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    first = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    }
    body = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
    }
    last = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    for item in (first, body, last):
        yield f"data: {json.dumps(item)}\n\n"
    yield "data: [DONE]\n\n"


def build_app(server: LocalHFServer) -> FastAPI:
    app = FastAPI(title="Local Hugging Face Model Server")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok" if server.model is not None else "loading",
            "model": server.model_id,
            "model_path": str(server.model_path),
            "precision": server.precision,
        }

    @app.get("/v1/models")
    def models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": server.model_id,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "local-huggingface",
                }
            ],
        }

    @app.post("/v1/chat/completions")
    def chat(request: ChatRequest) -> Any:
        if request.model != server.model_id:
            raise HTTPException(status_code=404, detail=f"Model not loaded: {request.model}")
        try:
            content = server.generate(request)
        except Exception as exc:  # pragma: no cover - runtime-specific model errors
            return JSONResponse(status_code=500, content={"error": {"message": str(exc)}})
        if request.stream:
            return StreamingResponse(stream_payload(server.model_id, content), media_type="text/event-stream")
        return completion_payload(server.model_id, content)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=sorted(MODEL_DEFAULTS), default="qwen3.8-27b")
    parser.add_argument("--precision", choices=("4bit", "bf16"), default="4bit")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = LocalHFServer(args.model, args.precision)
    server.load()
    app = build_app(server)
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
