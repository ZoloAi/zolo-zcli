# zCLI/subsystems/zData/zData_modules/paradigms/__init__.py
"""Data paradigm handlers - classical and quantum."""

from .classical.classical_data import ClassicalData
from .quantum.quantum_data import QuantumData

__all__ = [
    "ClassicalData",
    "QuantumData",
]

