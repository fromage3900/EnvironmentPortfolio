"""
Tests for Expanded Unreal Engine Blueprint & Python MCP Wrappers.

Validates:
1. Complete importability of expanded MCP wrapper modules (Animation, Audio, UI, Materials, Nodes, Blueprint, Editor, Project).
2. Schema integrity of all 95+ MCP tools (types, properties, required parameters, descriptions).
3. Tool handler routing and dispatch functionality.
4. Schema validation against representative payload invocations using jsonschema.
5. Mock execution pipeline and error handling.
"""

import asyncio
import json
import pytest
from typing import Any, Dict
try:
    import jsonschema
except ImportError:
    from scripts.benchmark_model_workflows import _JsonSchemaFallback as jsonschema

# Import the MCP server and tool modules
from ue_blueprint_mcp import server
from ue_blueprint_mcp.connection import CommandResult
from ue_blueprint_mcp.tools import (
    animation,
    audio,
    ui,
    umg,
    materials,
    nodes,
    blueprint,
    editor,
    project,
)


@pytest.fixture(scope="session")
def all_tools():
    """Retrieve all tools registered on the MCP server."""
    return asyncio.run(server.list_tools())


@pytest.fixture(scope="session")
def tool_map(all_tools):
    """Map tool names to Tool objects for quick lookup."""
    return {tool.name: tool for tool in all_tools}


# =============================================================================
# 1. Module Import & Registration Tests
# =============================================================================

def test_mcp_tool_modules_import():
    """Verify that all MCP wrapper subsystem modules are importable and have required interfaces."""
    modules = [animation, audio, ui, umg, materials, nodes, blueprint, editor, project]
    for mod in modules:
        assert hasattr(mod, "get_tools"), f"Module {mod.__name__} missing get_tools()"
        assert hasattr(mod, "handle_tool"), f"Module {mod.__name__} missing handle_tool()"
        assert hasattr(mod, "TOOL_HANDLERS"), f"Module {mod.__name__} missing TOOL_HANDLERS"
        assert isinstance(mod.TOOL_HANDLERS, dict), f"Module {mod.__name__} TOOL_HANDLERS is not a dict"


def test_server_list_tools_count(all_tools):
    """Verify that the server registers a substantial suite of tools (> 80 tools)."""
    assert len(all_tools) >= 90, f"Expected at least 90 registered tools, got {len(all_tools)}"


# =============================================================================
# 2. Schema Structure & Validation Tests
# =============================================================================

def test_all_tools_schema_conformance(all_tools):
    """Verify that every registered tool satisfies the MCP Tool schema specifications."""
    for tool in all_tools:
        assert tool.name and isinstance(tool.name, str), f"Tool {tool} has invalid name"
        assert tool.description and isinstance(tool.description, str), f"Tool {tool.name} has invalid description"
        assert isinstance(tool.inputSchema, dict), f"Tool {tool.name} inputSchema is not a dict"
        assert tool.inputSchema.get("type") == "object", f"Tool {tool.name} inputSchema type must be 'object'"
        assert "properties" in tool.inputSchema, f"Tool {tool.name} inputSchema missing 'properties'"


def test_animation_subsystem_schemas(tool_map):
    """Verify schema specifications for the Animation subsystem tools."""
    expected_anim_tools = [
        "create_animation_blueprint",
        "add_anim_state_machine",
        "add_anim_state",
        "add_anim_transition",
        "add_blend_space_player",
        "add_sequence_player",
        "add_bone_transform_node",
        "add_two_bone_ik_node",
        "add_anim_notify",
        "connect_anim_nodes",
        "get_anim_state_machine_states",
    ]

    for tool_name in expected_anim_tools:
        assert tool_name in tool_map, f"Animation tool '{tool_name}' missing from server registry"
        tool = tool_map[tool_name]
        schema = tool.inputSchema

        # Check required fields
        if tool_name == "create_animation_blueprint":
            assert "blueprint_name" in schema["properties"]
            assert "target_skeleton" in schema["properties"]
            assert "blueprint_name" in schema.get("required", [])
            assert "target_skeleton" in schema.get("required", [])
        elif tool_name == "add_anim_state_machine":
            assert "blueprint_name" in schema["properties"]
            assert "state_machine_name" in schema["properties"]
            assert "blueprint_name" in schema.get("required", [])
        elif tool_name == "add_anim_transition":
            assert "source_state" in schema["properties"]
            assert "target_state" in schema["properties"]
            assert "blend_time" in schema["properties"]
        elif tool_name == "add_bone_transform_node":
            assert "bone_name" in schema["properties"]
            assert "transform_mode" in schema["properties"]


def test_audio_subsystem_schemas(tool_map):
    """Verify schema specifications for the Audio & MetaSound subsystem tools."""
    expected_audio_tools = [
        "create_sound_cue",
        "add_sound_node_wave_player",
        "add_sound_node_modulator",
        "add_sound_node_random",
        "add_sound_node_attenuation",
        "create_metasound_source",
        "add_metasound_node",
        "connect_metasound_nodes",
        "set_metasound_parameter",
        "play_sound_at_location",
    ]

    for tool_name in expected_audio_tools:
        assert tool_name in tool_map, f"Audio tool '{tool_name}' missing from server registry"
        tool = tool_map[tool_name]
        schema = tool.inputSchema

        if tool_name == "create_sound_cue":
            assert "cue_name" in schema["properties"]
            assert "cue_name" in schema.get("required", [])
        elif tool_name == "create_metasound_source":
            assert "metasound_name" in schema["properties"]
            assert "output_format" in schema["properties"]
            assert "metasound_name" in schema.get("required", [])
        elif tool_name == "add_metasound_node":
            assert "node_type" in schema["properties"]
            assert "node_name" in schema["properties"]
        elif tool_name == "connect_metasound_nodes":
            assert "source_node" in schema["properties"]
            assert "source_pin" in schema["properties"]
            assert "target_node" in schema["properties"]
            assert "target_pin" in schema.get("required", [])


def test_ui_subsystem_schemas(tool_map):
    """Verify schema specifications for the UI & UMG subsystem tools."""
    expected_ui_tools = [
        "create_umg_widget_blueprint",
        "add_text_block_to_widget",
        "add_button_to_widget",
        "add_progress_bar_to_widget",
        "add_image_to_widget",
        "add_canvas_panel_slot",
        "create_widget_animation",
        "add_widget_animation_track",
        "play_widget_animation",
        "bind_widget_event",
        "add_widget_to_viewport",
        "set_text_block_binding",
    ]

    for tool_name in expected_ui_tools:
        assert tool_name in tool_map, f"UI tool '{tool_name}' missing from server registry"
        tool = tool_map[tool_name]
        schema = tool.inputSchema

        if tool_name == "add_progress_bar_to_widget":
            assert "widget_name" in schema["properties"]
            assert "progress_bar_name" in schema["properties"]
            assert "percent" in schema["properties"]
        elif tool_name == "add_canvas_panel_slot":
            assert "widget_name" in schema["properties"]
            assert "child_widget_name" in schema["properties"]
            assert "anchors" in schema["properties"]
            assert "alignment" in schema["properties"]
        elif tool_name == "create_widget_animation":
            assert "widget_name" in schema["properties"]
            assert "animation_name" in schema["properties"]
            assert "duration" in schema["properties"]


# =============================================================================
# 3. Payload Validation with JSONSchema
# =============================================================================

def test_sample_payload_validation(tool_map):
    """Validate sample realistic payloads against the schemas using jsonschema validator."""
    sample_payloads = [
        (
            "create_animation_blueprint",
            {
                "blueprint_name": "ABP_Melusina_Main",
                "target_skeleton": "/Game/Characters/Melusina/SK_Melusina_Skeleton",
                "parent_class": "AnimInstance",
                "path": "/Game/Animations"
            }
        ),
        (
            "add_anim_state_machine",
            {
                "blueprint_name": "ABP_Melusina_Main",
                "state_machine_name": "SM_Locomotion",
                "node_position": [200.0, 100.0]
            }
        ),
        (
            "add_anim_transition",
            {
                "blueprint_name": "ABP_Melusina_Main",
                "state_machine_name": "SM_Locomotion",
                "source_state": "Idle",
                "target_state": "Run",
                "transition_rule": "Speed > 10.0",
                "blend_time": 0.25
            }
        ),
        (
            "create_metasound_source",
            {
                "metasound_name": "MS_Melusina_RhythmSynth",
                "output_format": "Stereo",
                "path": "/Game/Audio/MetaSounds"
            }
        ),
        (
            "add_metasound_node",
            {
                "metasound_name": "MS_Melusina_RhythmSynth",
                "node_type": "SineGenerator",
                "node_name": "SineOsc_Lead",
                "node_position": [100.0, 50.0],
                "default_inputs": {"Frequency": 440.0}
            }
        ),
        (
            "add_progress_bar_to_widget",
            {
                "widget_name": "WBP_Melodia_HUD",
                "progress_bar_name": "HealthBar",
                "percent": 0.85,
                "fill_color": [0.2, 0.8, 0.4, 1.0],
                "position": [50.0, 50.0],
                "size": [300.0, 24.0]
            }
        ),
        (
            "create_widget_animation",
            {
                "widget_name": "WBP_Melodia_HUD",
                "animation_name": "PulseEffect",
                "duration": 0.6,
                "loop_count": 1
            }
        )
    ]

    for tool_name, payload in sample_payloads:
        tool = tool_map[tool_name]
        # jsonschema.validate will raise an exception if invalid
        jsonschema.validate(instance=payload, schema=tool.inputSchema)


# =============================================================================
# 4. Handler Dispatch & Mock Execution Tests
# =============================================================================

def test_server_call_tool_dispatch(monkeypatch):
    """Test calling server.call_tool with a mock connection."""
    recorded_commands = []

    class MockConnection:
        is_connected = True

        def connect(self):
            return True

        def send_command(self, command_type: str, params: dict | None = None):
            recorded_commands.append((command_type, params))
            return CommandResult(success=True, data={"mock_executed": True, "command": command_type})

        def ping(self):
            return True

    mock_conn = MockConnection()
    monkeypatch.setattr("ue_blueprint_mcp.server.get_connection", lambda: mock_conn)
    monkeypatch.setattr("ue_blueprint_mcp.tools.animation.get_connection", lambda: mock_conn)
    monkeypatch.setattr("ue_blueprint_mcp.tools.audio.get_connection", lambda: mock_conn)
    monkeypatch.setattr("ue_blueprint_mcp.tools.ui.get_connection", lambda: mock_conn)
    monkeypatch.setattr("ue_blueprint_mcp.tools.umg.get_connection", lambda: mock_conn)

    # Test Animation Tool Call
    res_anim = asyncio.run(server.call_tool(
        "create_animation_blueprint",
        {"blueprint_name": "ABP_Test", "target_skeleton": "SK_Test"}
    ))
    assert len(res_anim) == 1
    data_anim = json.loads(res_anim[0].text)
    assert data_anim["success"] is True

    # Test Audio Tool Call
    res_audio = asyncio.run(server.call_tool(
        "create_metasound_source",
        {"metasound_name": "MS_Test", "output_format": "Stereo"}
    ))
    assert len(res_audio) == 1
    data_audio = json.loads(res_audio[0].text)
    assert data_audio["success"] is True

    # Test UI Tool Call
    res_ui = asyncio.run(server.call_tool(
        "add_progress_bar_to_widget",
        {"widget_name": "WBP_Test", "progress_bar_name": "TestBar"}
    ))
    assert len(res_ui) == 1
    data_ui = json.loads(res_ui[0].text)
    assert data_ui["success"] is True

    # Verify command types recorded
    command_types = [cmd[0] for cmd in recorded_commands]
    assert "create_animation_blueprint" in command_types
    assert "create_metasound_source" in command_types
    assert "add_progress_bar_to_widget" in command_types


def test_unknown_tool_error_handling():
    """Verify that calling an unregistered tool returns an error structure."""
    result = asyncio.run(server.call_tool("invalid_nonexistent_tool", {}))
    assert len(result) == 1
    payload = json.loads(result[0].text)
    assert payload["success"] is False
    assert "Unknown tool" in payload["error"]


# =============================================================================
# 5. Adversarial Boundary & Invalid Payload Tests
# =============================================================================

def test_invalid_payloads_rejected_by_schema(tool_map):
    """Adversarially verify that invalid payloads fail JSONSchema validation."""
    invalid_cases = [
        # Missing required parameter: 'target_skeleton'
        (
            "create_animation_blueprint",
            {"blueprint_name": "ABP_Invalid"},
            "target_skeleton"
        ),
        # Invalid enum: 'transform_mode' must be ReplaceExisting, Additive, or Ignore
        (
            "add_bone_transform_node",
            {
                "blueprint_name": "ABP_Melusina",
                "bone_name": "tail_01",
                "transform_mode": "InvalidNonExistentMode"
            },
            "transform_mode"
        ),
        # Invalid enum: 'output_format' must be Mono, Stereo, Quad, 5.1, or 7.1
        (
            "create_metasound_source",
            {
                "metasound_name": "MS_Invalid",
                "output_format": "Octophonic_Atmos"
            },
            "output_format"
        ),
        # Invalid enum: 'parameter_type' must be Float, Int32, Boolean, Audio, Trigger, String
        (
            "set_metasound_parameter",
            {
                "metasound_name": "MS_Test",
                "parameter_name": "Cutoff",
                "parameter_type": "ComplexMatrix"
            },
            "parameter_type"
        ),
        # Type mismatch: 'percent' must be number, not string
        (
            "add_progress_bar_to_widget",
            {
                "widget_name": "WBP_Test",
                "progress_bar_name": "HealthBar",
                "percent": "half_full"
            },
            "percent"
        ),
        # Type mismatch: 'anchors' must be array, not string
        (
            "add_canvas_panel_slot",
            {
                "widget_name": "WBP_Test",
                "child_widget_name": "Portrait",
                "anchors": "center_fill"
            },
            "anchors"
        ),
        # Invalid enum: 'play_mode' must be Forward, Reverse, PingPong
        (
            "play_widget_animation",
            {
                "widget_name": "WBP_Test",
                "animation_name": "FadeIn",
                "play_mode": "SpiralBounce"
            },
            "play_mode"
        ),
        # Missing required parameter: 'target_pin'
        (
            "connect_anim_nodes",
            {
                "blueprint_name": "ABP_Test",
                "source_node": "NodeA",
                "source_pin": "Pose",
                "target_node": "NodeB"
            },
            "target_pin"
        ),
        # Missing required parameter: 'source_state'
        (
            "add_anim_transition",
            {
                "blueprint_name": "ABP_Test",
                "state_machine_name": "SM_Loco",
                "target_state": "Walk"
            },
            "source_state"
        )
    ]

    for tool_name, bad_payload, offending_field in invalid_cases:
        assert tool_name in tool_map, f"Tool '{tool_name}' not registered"
        schema = tool_map[tool_name].inputSchema
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(instance=bad_payload, schema=schema)
        assert offending_field in str(excinfo.value) or "required" in str(excinfo.value).lower(), (
            f"Expected validation failure on field '{offending_field}' for tool '{tool_name}'"
        )


def test_all_tools_schema_properties_types(all_tools):
    """Verify that all properties in every registered tool have valid schema definitions."""
    valid_types = {"string", "number", "integer", "boolean", "array", "object"}
    for tool in all_tools:
        props = tool.inputSchema.get("properties", {})
        for prop_name, prop_spec in props.items():
            assert isinstance(prop_spec, dict), f"Tool {tool.name}.{prop_name} specification is not a dict"
            prop_type = prop_spec.get("type")
            # If type is specified, it must be a valid JSONSchema type
            if prop_type is not None:
                assert prop_type in valid_types, f"Tool {tool.name}.{prop_name} has unknown type '{prop_type}'"
            # If array type, items spec should exist
            if prop_type == "array":
                assert "items" in prop_spec, f"Tool {tool.name}.{prop_name} is array type but missing 'items'"


def test_fallback_validator_compatibility(tool_map):
    """Verify that the standalone fallback validator accurately catches schema errors."""
    from scripts.benchmark_model_workflows import _JsonSchemaFallback

    valid_payload = {
        "blueprint_name": "ABP_Melusina_Valid",
        "target_skeleton": "/Game/Characters/SK_Melusina",
        "parent_class": "AnimInstance"
    }
    schema = tool_map["create_animation_blueprint"].inputSchema
    # Valid payload should pass
    _JsonSchemaFallback.validate(valid_payload, schema)

    # Missing required field should raise ValidationError
    bad_payload = {"blueprint_name": "ABP_Melusina_Valid"}
    with pytest.raises(_JsonSchemaFallback.ValidationError) as excinfo:
        _JsonSchemaFallback.validate(bad_payload, schema)
    assert "target_skeleton" in str(excinfo.value)


def test_fallback_validator_strictness(tool_map):
    """Verify fallback validator catches boolean-for-number, invalid enum, and non-dict inputs."""
    from scripts.benchmark_model_workflows import _JsonSchemaFallback

    # 1. Boolean passed for number (Python's bool is subclass of int)
    prog_schema = tool_map["add_progress_bar_to_widget"].inputSchema
    bad_number_payload = {
        "widget_name": "WBP_Test",
        "progress_bar_name": "Bar",
        "percent": True  # boolean should fail number check
    }
    with pytest.raises(_JsonSchemaFallback.ValidationError) as excinfo:
        _JsonSchemaFallback.validate(bad_number_payload, prog_schema)
    assert "percent" in str(excinfo.value)

    # 2. String array items when number items expected
    pos_schema = tool_map["add_anim_state_machine"].inputSchema
    bad_array_items_payload = {
        "blueprint_name": "ABP_Test",
        "state_machine_name": "SM_Test",
        "node_position": ["invalid_str", "pos"]  # string items when number expected
    }
    with pytest.raises(_JsonSchemaFallback.ValidationError) as excinfo:
        _JsonSchemaFallback.validate(bad_array_items_payload, pos_schema)
    assert "node_position" in str(excinfo.value)

    # 3. Invalid enum value
    bone_schema = tool_map["add_bone_transform_node"].inputSchema
    bad_enum_payload = {
        "blueprint_name": "ABP_Test",
        "bone_name": "tail_01",
        "transform_mode": "InvalidMode"
    }
    with pytest.raises(_JsonSchemaFallback.ValidationError) as excinfo:
        _JsonSchemaFallback.validate(bad_enum_payload, bone_schema)
    assert "transform_mode" in str(excinfo.value)

