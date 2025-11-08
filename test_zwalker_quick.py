# Quick test for zWalker tests
import sys
from zCLI import zCLI

# Initialize zCLI
zcli_instance = zCLI(zspark_dict={"zVaFile": "@.zUI.zWalker_tests", "zBlock": "zVaF"})

# Run walker tests
print("\n" + "="*70)
print("Running zWalker Tests...")
print("="*70 + "\n")

try:
    result = zcli_instance.walker.run()
    print(f"\nResult: {result}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
