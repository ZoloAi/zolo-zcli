from zCLI import zCLI

z = zCLI()

print(f"Mode: {z.session.get('zMode', 'Unknown')}")
print(f"display.mode: {z.display.mode}")
print(f"_is_gui_mode(): {z.display.zEvents.BasicInputs.zPrimitives._is_gui_mode()}")

