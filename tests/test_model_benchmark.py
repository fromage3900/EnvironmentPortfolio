"""
Tests for Melodia Model Workflow Evaluation & Blueprint Benchmark Harness.

Validates:
1. Automated benchmark script runs across Qwen and Muse Glimmer models.
2. Procedural logic generation produces valid Blueprint fixtures across all subsystems (Animation, Audio, UI, Core Graph).
3. 100% schema compliance and >95% benchmark pass rate.
4. Evaluation reports (eval_results.json, MODEL_WORKFLOW_EVALUATION_REPORT.md) and fixtures are saved to repository.
"""

import asyncio
import json
from pathlib import Path
import pytest

from scripts import benchmark_model_workflows


@pytest.fixture(scope="session")
def benchmark_results():
    """Run benchmark harness across Qwen and Muse Glimmer models and return summary."""
    models = ["qwen3.8-27b", "qwen2.5-coder:7b", "muse-glimmer-30b"]
    summary = asyncio.run(benchmark_model_workflows.run_benchmark(models=models))
    return summary


def test_benchmark_execution_and_pass_rate(benchmark_results):
    """Verify that all benchmark tasks execute successfully with a high pass rate."""
    assert benchmark_results["total_evaluations"] >= 9
    assert benchmark_results["pass_rate_percent"] >= 95.0
    assert benchmark_results["average_score"] >= 90.0


def test_benchmark_subsystem_coverage(benchmark_results):
    """Verify that evaluations covered Animation, Audio, UI, and GameplayLogic subsystems."""
    subsystems_tested = {r["subsystem"] for r in benchmark_results["results"]}
    expected_subsystems = {"Animation", "Audio", "UI", "GameplayLogic"}
    assert expected_subsystems.issubset(subsystems_tested), f"Missing subsystem evaluations: {expected_subsystems - subsystems_tested}"


def test_benchmark_schema_compliance(benchmark_results):
    """Verify that every evaluated model output achieves 100% schema compliance."""
    for result in benchmark_results["results"]:
        assert result["schema_compliance_rate"] == 100.0, f"Model {result['model_id']} on {result['task_id']} had schema errors: {result['errors']}"
        assert result["total_score"] >= 85.0


def test_fixtures_and_reports_written_to_repo():
    """Verify that generated fixtures, JSON manifest, and Markdown reports exist on disk."""
    repo_root = Path(__file__).resolve().parent.parent

    # Check root eval_results.json
    eval_json = repo_root / "eval_results.json"
    assert eval_json.exists(), "Root eval_results.json was not created"
    data = json.loads(eval_json.read_text(encoding="utf-8"))
    assert "results" in data and len(data["results"]) > 0

    # Check Markdown report
    doc_report = repo_root / "docs" / "MODEL_WORKFLOW_EVALUATION_REPORT.md"
    assert doc_report.exists(), "docs/MODEL_WORKFLOW_EVALUATION_REPORT.md was not created"
    report_content = doc_report.read_text(encoding="utf-8")
    assert "Melodia Melusina AI Pipeline" in report_content
    assert "Animation Subsystem" in report_content or "Animation" in report_content
    assert "MetaSound" in report_content or "Audio" in report_content

    # Check saved fixtures directory
    fixtures_dir = repo_root / "BS_GodFile" / "Fixtures" / "Blueprints"
    assert fixtures_dir.exists(), "BS_GodFile/Fixtures/Blueprints directory missing"
    manifest = fixtures_dir / "fixtures_manifest.json"
    assert manifest.exists(), "fixtures_manifest.json was not created"

    fixtures_list = list(fixtures_dir.glob("*.json"))
    assert len(fixtures_list) >= 4, f"Expected multiple generated Blueprint fixture files, found {len(fixtures_list)}"


# =============================================================================
# Adversarial Evaluator Logic Tests
# =============================================================================

def test_evaluator_catches_schema_violations_and_penalizes():
    """Verify that the benchmark evaluator penalizes schema violations and fails task."""
    from ue_blueprint_mcp import server
    tools = asyncio.run(server.list_tools())
    schemas = {tool.name: tool for tool in tools}
    evaluator = benchmark_model_workflows.ModelWorkflowEvaluator(schemas)
    task = benchmark_model_workflows.BENCHMARK_TASKS[0]  # Animation task

    # Intentionally malformed tool calls
    bad_calls = [
        {
            "tool": "create_animation_blueprint",
            "arguments": {"invalid_field": 123}  # Missing blueprint_name and target_skeleton
        },
        {
            "tool": "add_anim_state_machine",
            "arguments": {"blueprint_name": "ABP_Test"}  # Missing state_machine_name
        }
    ]

    res = evaluator.evaluate_tool_calls(task, "failing_model", bad_calls, 50.0)
    assert res.success is False
    assert res.schema_compliance_rate < 50.0
    assert len(res.errors) > 0
    assert res.total_score < 70.0


def test_evaluator_catches_missing_required_tools():
    """Verify that evaluator flags missing required subsystem tools."""
    from ue_blueprint_mcp import server
    tools = asyncio.run(server.list_tools())
    schemas = {tool.name: tool for tool in tools}
    evaluator = benchmark_model_workflows.ModelWorkflowEvaluator(schemas)
    task = benchmark_model_workflows.BENCHMARK_TASKS[1]  # Audio task

    # Only provide create_metasound_source, leaving out all oscillator / dsp nodes
    partial_calls = [
        {
            "tool": "create_metasound_source",
            "arguments": {
                "metasound_name": "MS_Partial",
                "output_format": "Mono"
            }
        }
    ]

    res = evaluator.evaluate_tool_calls(task, "partial_model", partial_calls, 30.0)
    assert res.success is False
    assert any("Missing required subsystem tools" in err for err in res.errors)
    assert res.semantic_completeness_score < 60.0


def test_evaluator_handles_zero_tool_calls_gracefully():
    """Verify that evaluator does not crash on empty tool call list (0 calls)."""
    from ue_blueprint_mcp import server
    tools = asyncio.run(server.list_tools())
    schemas = {tool.name: tool for tool in tools}
    evaluator = benchmark_model_workflows.ModelWorkflowEvaluator(schemas)
    task = benchmark_model_workflows.BENCHMARK_TASKS[2]  # UI task

    res = evaluator.evaluate_tool_calls(task, "empty_model", [], 10.0)
    assert res.success is False
    assert res.total_score == 0.0
    assert res.schema_compliance_rate == 0.0
    assert res.nodes_generated == 0
    assert res.connections_generated == 0


def test_fixtures_content_and_manifest_validity():
    """Verify that all generated fixtures contain valid JSON structure and metadata."""
    repo_root = Path(__file__).resolve().parent.parent
    fixtures_dir = repo_root / "BS_GodFile" / "Fixtures" / "Blueprints"
    manifest_path = fixtures_dir / "fixtures_manifest.json"

    assert manifest_path.exists(), "Manifest missing"
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(manifest_data, list) and len(manifest_data) > 0

    for entry in manifest_data:
        assert "model" in entry
        assert "task_id" in entry
        assert "subsystem" in entry
        assert "fixture_file" in entry
        assert "score" in entry
        assert "success" in entry

        fixture_file = fixtures_dir / entry["fixture_file"]
        assert fixture_file.exists(), f"Fixture file '{entry['fixture_file']}' listed in manifest does not exist"
        fix_data = json.loads(fixture_file.read_text(encoding="utf-8"))
        assert "meta" in fix_data
        assert "pipeline_operations" in fix_data
        assert len(fix_data["pipeline_operations"]) > 0


def test_benchmark_dataclasses_type_hints_resolution():
    """Verify that runtime type hints on benchmark dataclasses and functions resolve without NameError."""
    import typing
    hints_task = typing.get_type_hints(benchmark_model_workflows.TaskDefinition)
    assert "required_tools" in hints_task
    hints_res = typing.get_type_hints(benchmark_model_workflows.EvaluationResult)
    assert "schema_compliance_rate" in hints_res
    hints_run = typing.get_type_hints(benchmark_model_workflows.run_benchmark)
    assert "models" in hints_run
    hints_report = typing.get_type_hints(benchmark_model_workflows.generate_markdown_report)
    assert "summary" in hints_report

