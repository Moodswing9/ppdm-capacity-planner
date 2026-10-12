"""
Tests for ppdm-capacity-planner / planner.py
"""
import sys
import os

# Ensure the project root is on the path so we can import planner
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import planner
from planner import (
    PPDMClient,
    build_prompt,
    format_system,
    parse_args,
    parse_storage_systems,
)


# ---------------------------------------------------------------------------
# test_version
# ---------------------------------------------------------------------------

def test_version():
    assert planner.__version__ == "1.0.1"


# ---------------------------------------------------------------------------
# test_demo_flag_parses
# ---------------------------------------------------------------------------

def test_demo_flag_parses():
    args = parse_args(["--demo"])
    assert args.demo is True


def test_demo_flag_absent_by_default():
    args = parse_args([])
    assert args.demo is False


# ---------------------------------------------------------------------------
# test_storage_system_format
# ---------------------------------------------------------------------------

_MOCK_SYSTEM = {
    "name": "TestArray",
    "total_gib": 1024.0,
    "used_gib": 768.0,
    "used_pct": 75.0,
}


def test_storage_system_format_gib():
    result = format_system(_MOCK_SYSTEM)
    assert "768.0 GiB" in result
    assert "1024.0 GiB" in result


def test_storage_system_format_percentage():
    result = format_system(_MOCK_SYSTEM)
    assert "75.0%" in result


def test_storage_system_format_name():
    result = format_system(_MOCK_SYSTEM)
    assert "TestArray" in result


# ---------------------------------------------------------------------------
# test_build_prompt_contains_systems
# ---------------------------------------------------------------------------

_MULTI_SYSTEMS = [
    {"name": "Alpha", "total_gib": 500.0, "used_gib": 100.0, "used_pct": 20.0},
    {"name": "Beta",  "total_gib": 1000.0, "used_gib": 900.0, "used_pct": 90.0},
    {"name": "Gamma", "total_gib": 2000.0, "used_gib": 1100.0, "used_pct": 55.0},
]


def test_build_prompt_contains_systems():
    prompt = build_prompt(_MULTI_SYSTEMS)
    for system in _MULTI_SYSTEMS:
        assert system["name"] in prompt


def test_build_prompt_mentions_thresholds():
    prompt = build_prompt(_MULTI_SYSTEMS)
    assert "80%" in prompt
    assert "95%" in prompt


def test_build_prompt_mentions_recommendations():
    prompt = build_prompt(_MULTI_SYSTEMS)
    assert "Recommendations" in prompt or "recommendations" in prompt


# ---------------------------------------------------------------------------
# test_ppdm_client_init
# ---------------------------------------------------------------------------

def test_ppdm_client_init():
    client = PPDMClient(host="test", user="u", password="p")
    assert client.host == "test"
    assert client.user == "u"
    assert client.password == "p"
    assert client.port == 8443
    assert client.token is None


def test_ppdm_client_custom_port():
    client = PPDMClient(host="ppdm.local", user="admin", password="secret", port=9443)
    assert client.port == 9443
    assert client.base_url == "https://ppdm.local:9443/api/v2"


# ---------------------------------------------------------------------------
# test_parse_storage_systems
# ---------------------------------------------------------------------------

def test_parse_storage_systems_basic():
    raw = [
        {
            "name": "ArrayOne",
            "totalCapacity": 2048.0,
            "usedCapacity": 1024.0,
            "usedPercentage": 50.0,
        }
    ]
    result = parse_storage_systems(raw)
    assert len(result) == 1
    assert result[0]["name"] == "ArrayOne"
    assert result[0]["total_gib"] == 2048.0
    assert result[0]["used_gib"] == 1024.0
    assert result[0]["used_pct"] == 50.0


def test_parse_storage_systems_calculates_pct():
    """usedPercentage absent — should be calculated from totalCapacity/usedCapacity."""
    raw = [
        {
            "name": "ArrayTwo",
            "totalCapacity": 1000.0,
            "usedCapacity": 250.0,
        }
    ]
    result = parse_storage_systems(raw)
    assert abs(result[0]["used_pct"] - 25.0) < 0.01
