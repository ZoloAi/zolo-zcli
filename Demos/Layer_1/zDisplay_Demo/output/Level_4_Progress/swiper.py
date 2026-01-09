#!/usr/bin/env python3
"""
Level 5: Swiper (Interactive Slideshow)
========================================

Goal:
    Learn swiper() for interactive content carousels.
    - Auto-advancing slides with configurable delay
    - Manual navigation (arrow keys, number keys)
    - Pause/Resume functionality
    - Beautiful box-drawn UI
    - Perfect for tutorials, onboarding, presentations

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/swiper.py
"""

import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zKernel import zKernel

def run_demo():
    """Demonstrate swiper interactive slideshow."""
    z = zKernel({"logger": "PROD"})
    
    z.display.line("")
    z.display.line("=== Level 5: Swiper (Interactive Slideshow) ===")
    z.display.line("")
    
    # ============================================
    # 1. Simple Auto-Advancing Swiper
    # ============================================
    z.display.header("Simple Auto-Advancing Swiper", color="CYAN", indent=0)
    z.display.text("Basic slideshow with 3-second intervals:")
    z.display.text("")
    
    intro_slides = [
        "Welcome to zCLI!",
        "zCLI is a dual-mode CLI framework",
        "Works in Terminal and Browser (zBifrost)",
        "Let's explore the features..."
    ]
    
    z.display.text("Starting slideshow (press 'q' to skip)...")
    z.display.text("")
    z.display.zEvents.TimeBased.swiper(intro_slides, "Introduction", auto_advance=True, delay=3)
    
    z.display.text("")
    z.display.success("✅ Slideshow complete!")
    z.display.text("")
    
    # ============================================
    # 2. Tutorial with Manual Control
    # ============================================
    z.display.header("Tutorial with Manual Control", color="GREEN", indent=0)
    z.display.text("Navigate with arrow keys, pause with 'p', quit with 'q':")
    z.display.text("")
    
    tutorial_slides = [
        "Step 1: Initialize zCLI\n\n  from zKernel import zCLI\n  z = zKernel()",
        "Step 2: Display Progress Bar\n\n  z.display.progress_bar(50, 100, 'Processing')",
        "Step 3: Show Spinner\n\n  with z.display.spinner('Loading'):\n      time.sleep(2)",
        "Step 4: Create Interactive Tables\n\n  z.display.zTable(title='Users', columns=[...], rows=[...])",
        "You're ready to build dual-mode CLIs!"
    ]
    
    z.display.text("Starting tutorial (use ◀ ▶ arrows to navigate)...")
    z.display.text("")
    z.display.zEvents.TimeBased.swiper(tutorial_slides, "zCLI Tutorial", auto_advance=False)
    
    z.display.text("")
    z.display.success("✅ Tutorial complete!")
    z.display.text("")
    
    # ============================================
    # 3. Feature Showcase with Loop
    # ============================================
    z.display.header("Feature Showcase with Loop", color="YELLOW", indent=0)
    z.display.text("Auto-advancing slideshow with loop enabled:")
    z.display.text("")
    
    features = [
        "Feature 1: Progress Tracking\n\nVisual progress bars with ETA\nAutomatic progress iterators\nSmooth terminal rendering",
        "Feature 2: Loading Indicators\n\nAnimated spinners (6 styles)\nContext manager API\nNon-blocking operation",
        "Feature 3: Data Display\n\nTables with pagination\nJSON with syntax coloring\nHierarchical outlines",
        "Feature 4: Interactive Swipers\n\nAuto-advancing slides\nKeyboard navigation\nLoop mode support"
    ]
    
    z.display.text("Starting showcase (loops after last slide)...")
    z.display.text("")
    z.display.zEvents.TimeBased.swiper(features, "zDisplay Features", auto_advance=True, delay=4, loop=True)
    
    z.display.text("")
    z.display.success("✅ Showcase complete!")
    z.display.text("")
    
    # ============================================
    # 4. Real-World Example: Onboarding Flow
    # ============================================
    z.display.header("Real-World Example: Onboarding", color="BLUE", indent=0)
    z.display.text("Multi-step onboarding with jump-to functionality:")
    z.display.text("")
    
    onboarding = [
        "Welcome to MyApp!\n\nWe'll guide you through setup in 5 easy steps.\n\nPress ▶ to continue or jump with 1-5 keys",
        "Step 1: Create Account\n\n• Choose a username\n• Set a strong password\n• Verify your email",
        "Step 2: Personalize\n\n• Upload a profile picture\n• Set your preferences\n• Choose a theme",
        "Step 3: Connect Services\n\n• Link your GitHub account\n• Connect to Slack\n• Authorize API access",
        "Step 4: Invite Team\n\n• Send invitation emails\n• Assign roles\n• Set permissions",
        "All Done!\n\nYou're ready to start using MyApp.\n\nPress 'q' to finish setup."
    ]
    
    z.display.text("Starting onboarding (jump with number keys 1-6)...")
    z.display.text("")
    z.display.zEvents.TimeBased.swiper(onboarding, "MyApp Setup", auto_advance=False)
    
    z.display.text("")
    z.display.success("✅ Onboarding complete!")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ swiper() - Interactive slideshow/carousel")
    z.display.text("✓ auto_advance - Automatic slide progression")
    z.display.text("✓ Manual navigation - Arrow keys, number keys")
    z.display.text("✓ Pause/Resume - 'p' key toggles auto-advance")
    z.display.text("✓ Loop mode - Continuous cycling through slides")
    z.display.text("✓ Box-drawn UI - Beautiful bordered display")
    z.display.text("✓ Perfect for tutorials, onboarding, presentations")
    z.display.text("")
    
    z.display.line("Tip: Swipers make complex flows engaging and interactive!")
    z.display.line("")
    z.display.info("💡 Note: swiper accessed via z.display.zEvents.TimeBased.swiper()")
    z.display.line("")

if __name__ == "__main__":
    run_demo()

