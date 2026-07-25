"""Tests for quality-gate.py core functions."""

import sys
import os
import importlib.util

# Import quality-gate.py (hyphen in filename prevents normal import)
spec = importlib.util.spec_from_file_location(
    "quality_gate",
    os.path.join(os.path.dirname(__file__), "..", "scripts", "quality-gate.py")
)
qg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qg)
check_agent_misuse = qg.check_agent_misuse


def test_check_agent_misuse_empty_transcript():
    """Empty transcript should return no warnings."""
    result = check_agent_misuse("")
    assert result == []


def test_check_agent_misuse_no_agent_calls():
    """Transcript without Agent calls should return no warnings."""
    result = check_agent_misuse('{"role": "assistant", "content": "hello"}')
    assert result == []


def test_check_agent_misuse_detects_search_patterns():
    """Agent calls matching search patterns (like 'find files') should be flagged."""
    transcript = '{"name": "Agent", "description": "find files in project"}'
    result = check_agent_misuse(transcript)
    assert len(result) == 1
    assert "find files" in result[0]


def test_check_agent_misuse_semantic_skip():
    """Agent calls with semantic verbs should be skipped."""
    # "analyze", "review", "design" etc. are semantic stems that are allowed
    transcript = '{"name": "Agent", "description": "analyze codebase structure and review architecture"}'
    result = check_agent_misuse(transcript)
    assert result == []
