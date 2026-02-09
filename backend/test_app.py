import pytest
import os
import sys

# Add the current directory to the path so app can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import calculate_risk_level, get_compliance_hint

def test_risk_level_logic():
    # Test mapping ranges
    assert calculate_risk_level(1) == "Low"
    assert calculate_risk_level(5) == "Low"
    assert calculate_risk_level(6) == "Medium"
    assert calculate_risk_level(12) == "Medium"
    assert calculate_risk_level(13) == "High"
    assert calculate_risk_level(18) == "High"
    assert calculate_risk_level(19) == "Critical"
    assert calculate_risk_level(25) == "Critical"

def test_compliance_hints():
    # Test bonus hint triggering
    assert get_compliance_hint("Low") == ""
    assert get_compliance_hint("Medium") == ""
    assert "NIST" in get_compliance_hint("High")
    assert "NIST" in get_compliance_hint("Critical")

def test_invalid_score():
    assert calculate_risk_level(0) == "Unknown"
    assert calculate_risk_level(26) == "Unknown"
