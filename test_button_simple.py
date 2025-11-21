from zCLI import zCLI

z = zCLI()

print("\n=== Testing Button ===")
print(f"Mode: {z.session.get('zMode')}")
print(f"Display mode: {z.display.mode}")

print("\nCalling button...")
result = z.display.button("Test Button", color="success")

print(f"\nButton returned: {result}")
print(f"Type: {type(result)}")

