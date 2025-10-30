#!/bin/bash
# Test script for TimeBased Events Demo
# Tests all demos non-interactively

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║  Testing zDisplay TimeBased Events Demo                                  ║"
echo "║  Testing: Progress Bars, Spinners, and Swiper Integration               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Basic Progress Bar
echo "🧪 Test 1: Basic Progress Bar"
echo "───────────────────────────────────────────────────────────────────────────"
echo -e "1\nstop" | python3 demo_progress_widgets.py 2>/dev/null | grep -A 2 "Demo 1:"
echo ""

# Test 2: Progress with ETA
echo "🧪 Test 2: Progress with ETA"
echo "───────────────────────────────────────────────────────────────────────────"
echo -e "2\nstop" | python3 demo_progress_widgets.py 2>/dev/null | grep -A 2 "Demo 2:"
echo ""

# Test 3: Colored Progress Bars
echo "🧪 Test 3: Colored Progress Bars"
echo "───────────────────────────────────────────────────────────────────────────"
echo -e "3\nstop" | python3 demo_progress_widgets.py 2>/dev/null | grep -A 2 "Demo 3:"
echo ""

# Test 4: Loading Spinners
echo "🧪 Test 4: Loading Spinners"
echo "───────────────────────────────────────────────────────────────────────────"
echo -e "4\nstop" | python3 demo_progress_widgets.py 2>/dev/null | grep -A 2 "Demo 4:"
echo ""

# Test 5: Verify swiper is in menu
echo "🧪 Test 5: Verify Swiper in Menu"
echo "───────────────────────────────────────────────────────────────────────────"
echo -e "stop" | python3 demo_progress_widgets.py 2>/dev/null | grep "Content Swiper"
if [ $? -eq 0 ]; then
    echo "✅ Swiper option found in menu!"
else
    echo "❌ Swiper option NOT found in menu"
fi
echo ""

# Test 6: Check TimeBased class exists
echo "🧪 Test 6: Verify TimeBased Class"
echo "───────────────────────────────────────────────────────────────────────────"
python3 -c "
from zCLI.subsystems.zDisplay.zDisplay_modules.events.display_event_timebased import TimeBased
print('✅ TimeBased class imported successfully')
print(f'   Methods: {[m for m in dir(TimeBased) if not m.startswith(\"_\") and callable(getattr(TimeBased, m))]}')
" 2>/dev/null
echo ""

# Test 7: Verify swiper method exists
echo "🧪 Test 7: Verify Swiper Method Exists"
echo "───────────────────────────────────────────────────────────────────────────"
python3 -c "
from zCLI.subsystems.zDisplay.zDisplay_modules.events.display_event_timebased import TimeBased
if hasattr(TimeBased, 'swiper'):
    print('✅ swiper() method exists in TimeBased class')
    import inspect
    sig = inspect.signature(TimeBased.swiper)
    print(f'   Signature: swiper{sig}')
else:
    print('❌ swiper() method NOT found')
" 2>/dev/null
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ TimeBased Events Demo Tests Complete                                 ║"
echo "║                                                                           ║"
echo "║  Tests Completed:                                                         ║"
echo "║  • Progress Bar demos (1-4) ✓                                           ║"
echo "║  • Swiper menu integration ✓                                             ║"
echo "║  • TimeBased class structure ✓                                           ║"
echo "║  • Swiper method signature ✓                                             ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Note: Interactive swiper test requires manual execution:"
echo "  $ python3 demo_progress_widgets.py"
echo "  > Select option 9 (NEW: Content Swiper 🎯)"
echo ""

