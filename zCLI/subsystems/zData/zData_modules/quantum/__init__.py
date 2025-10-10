# zCLI/subsystems/zData/zData_modules/quantum/__init__.py
# ----------------------------------------------------------------
# Quantum data management package.
# 
# Handles abstracted data structures using zStrongNuclearField
# for identity and temporality management.
# ----------------------------------------------------------------

from .quantum_data import QuantumData

__all__ = [
    'QuantumData',
]

