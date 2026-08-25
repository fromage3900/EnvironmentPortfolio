#!/usr/bin/env python3
"""Test Bedrock model invocation using the bedrock AWS profile."""
import sys
import os

import boto3
from botocore.config import Config

session = boto3.Session(profile_name="bedrock", region_name="us-east-1")
rt = session.client("bedrock-runtime", config=Config(retries={"max_attempts": 3, "mode": "adaptive"}))

models = [
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "qwen.qwen3-coder-next",
    "nvidia.nemotron-nano-12b-v2",
    "anthropic.claude-haiku-4-5-20251001-v1:0",
]

print("Testing Bedrock model invocations with bedrock profile...", file=sys.stderr, flush=True)

for model_id in models:
    try:
        print("  Testing " + model_id + "...", file=sys.stderr, flush=True)
        response = rt.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Hello! Reply with just: OK"}]}],
            inferenceConfig={"maxTokens": 32, "temperature": 0.1},
        )
        text = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})
        print("  OK " + model_id + ": " + text.strip() + " (in=" + str(usage.get("inputTokens", "?")) + ", out=" + str(usage.get("outputTokens", "?")) + ")", flush=True)
    except Exception as e:
        emsg = str(e)[:200]
        print("  FAIL " + model_id + ": " + emsg, flush=True)

print("\nDone.", file=sys.stderr, flush=True)