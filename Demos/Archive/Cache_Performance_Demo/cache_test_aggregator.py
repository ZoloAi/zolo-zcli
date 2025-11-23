"""
Cache Test Aggregator Plugin for zCLI

Processes zHat results from cache performance tests and formats them
for display in the frontend.
"""

import time
from datetime import datetime


def aggregate_results(zHat):
    """
    Aggregate cache test results from zWizard steps.
    
    Args:
        zHat: List of results from each zWizard step
        
    Returns:
        dict: Formatted test results for frontend display
    """
    
    # Extract timing information (if available from zDisplay/zData metadata)
    # For now, we'll return the raw data and let frontend measure timing
    
    results = {
        "test_suite": "zBifrost Cache Performance",
        "timestamp": datetime.now().isoformat(),
        "tests": [
            {
                "name": "System Cache Test (Miss)",
                "step": "system_cache_miss",
                "data": zHat[0] if len(zHat) > 0 else None,
                "records": len(zHat[0]) if zHat and zHat[0] and isinstance(zHat[0], list) else 0
            },
            {
                "name": "System Cache Test (Hit)",
                "step": "system_cache_hit",
                "data": zHat[1] if len(zHat) > 1 else None,
                "records": len(zHat[1]) if len(zHat) > 1 and zHat[1] and isinstance(zHat[1], list) else 0
            },
            {
                "name": "Query Cache Test",
                "step": "query_cache_test",
                "data": zHat[2] if len(zHat) > 2 else None,
                "records": len(zHat[2]) if len(zHat) > 2 and zHat[2] and isinstance(zHat[2], list) else 0
            }
        ],
        "summary": {
            "total_steps": len(zHat),
            "successful_steps": sum(1 for item in zHat if item is not None),
            "data_consistent": _check_consistency(zHat)
        }
    }
    
    return results


def _check_consistency(zHat):
    """Check if all cache requests returned the same data."""
    if not zHat or len(zHat) < 2:
        return True
    
    # Compare first two results (should be identical if cache works)
    first = zHat[0]
    second = zHat[1]
    
    if not first or not second:
        return False
    
    # Simple length check
    if isinstance(first, list) and isinstance(second, list):
        return len(first) == len(second)
    
    return first == second


# Plugin metadata
__plugin_name__ = "cache_test_aggregator"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Aggregates cache test results from zWizard sequences"

