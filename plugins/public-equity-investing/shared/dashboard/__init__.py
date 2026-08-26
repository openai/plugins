"""Shared Public Equity Investing dashboard rendering utilities."""

from .qa import validate_payload
from .renderer import render_dashboard

__all__ = ["render_dashboard", "validate_payload"]
