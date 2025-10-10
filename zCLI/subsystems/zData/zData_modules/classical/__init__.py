# zCLI/subsystems/zData/zData_modules/classical/__init__.py
# ----------------------------------------------------------------
# Classical data management package.
# 
# Handles conventional data structures with explicit id, timestamps,
# and traditional relational database patterns.
# ----------------------------------------------------------------

from .classical_data import ClassicalData

__all__ = [
    'ClassicalData',
]