"""
Package initialization for the Task Management System API.

This module initializes the FastAPI application and makes all submodules available.
"""

from .main import app

__all__ = ["app"]