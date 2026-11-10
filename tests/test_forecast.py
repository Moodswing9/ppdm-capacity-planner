"""generate_forecast(): request settings and response handling (Claude mocked)."""
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import planner

SYSTEMS = planner.parse_storage_systems(planner.DEMO_SYSTEMS_RAW)


def _response(*blocks, stop_reason="end_turn"):
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(**b) for b in blocks])


@pytest.fixture
def client():
    with patch("planner.anthropic.Anthropic") as cls:
        mock = MagicMock()
        cls.return_value = mock
        yield mock


def test_targets_opus_5_5_at_low_effort(client):
    client.beta.messages.create.return_value = _response({"type": "text", "text": "ok"})
    planner.generate_forecast(SYSTEMS)
    kwargs = client.beta.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-opus-5-5"
    assert kwargs["output_config"] == {"effort": "low"}
    assert kwargs["fallbacks"] == "default"
    assert "server-side-fallback-2026-07-01" in kwargs["betas"]


def test_leaves_room_for_thinking_and_the_full_report(client):
    # 1024 cut the report off before the Executive Summary on Opus 4.7.
    client.beta.messages.create.return_value = _response({"type": "text", "text": "ok"})
    planner.generate_forecast(SYSTEMS)
    assert client.beta.messages.create.call_args.kwargs["max_tokens"] >= 8000


def test_reads_text_after_a_thinking_block(client):
    client.beta.messages.create.return_value = _response(
        {"type": "thinking", "thinking": ""},
        {"type": "text", "text": "## Breach projections"},
    )
    assert planner.generate_forecast(SYSTEMS) == "## Breach projections"


def test_flags_a_truncated_report(client):
    client.beta.messages.create.return_value = _response(
        {"type": "text", "text": "## Breach projections"}, stop_reason="max_tokens"
    )
    assert "cut off" in planner.generate_forecast(SYSTEMS)


def test_refusal_raises_forecast_error(client):
    client.beta.messages.create.return_value = _response(stop_reason="refusal")
    with pytest.raises(planner.ForecastError):
        planner.generate_forecast(SYSTEMS)


def test_main_exits_3_on_refusal(client, capsys):
    client.beta.messages.create.return_value = _response(stop_reason="refusal")
    assert planner.main(["--demo"]) == 3
    assert "declined" in capsys.readouterr().err
