from __future__ import annotations

import sqlite3

from src.run_registry import classify_error_class


def test_classify_error_class_marks_locked_operational_error_as_transient():
    exc = sqlite3.OperationalError("database is locked")
    assert classify_error_class(exc) == "transient"


def test_classify_error_class_marks_other_errors_as_permanent():
    assert classify_error_class(RuntimeError("boom")) == "permanent"
    assert classify_error_class(sqlite3.OperationalError("some other sqlite problem")) == "permanent"
