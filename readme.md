# Monitor Controller for BenQ MOBIUZ EX321UX
Hardware DDC/CI control for BenQ monitors using Behringer X-Touch Mini.

## Features
- Brightness control (knob 1)
- Night mode with warm color shift (knob 2)
- Local dimming toggle (button 8)
- HDR toggle (button 9)

## Hardware Requirements
- BenQ MOBIUZ EX321UX monitor (or similar with DDC/CI)
- Behringer X-Touch Mini MIDI controller

## Limitations

### Undocumented VCP Codes
The BenQ MOBIUZ EX321UX uses manufacturer-specific VCP codes for some features. We've discovered:

- **0xEA**: Local Dimming (0=Off, 1=On) ✓ Confirmed
- **0x10**: Brightness ✓ Standard
- **0x1A, 0x16, 0x18**: RGB Gains (for night mode) ✓ Standard
- **0x87**: Sharpness ✓ Standard

**Unknown/Untested:**
- Black eQualizer
- Response Time / Overdrive
- Picture Mode switching
- HDR toggle via DDC

If you discover additional VCP codes for this monitor, please let me know!

### Monitor Compatibility
This software is designed for the **BenQ MOBIUZ EX321UX** but may work with other BenQ monitors that support DDC/CI. Features like Local Dimming may not work on monitors without that specific VCP code.

## Installation
1. Download `MonitorController.exe` from [dist](https://github.com/4AM365/midi-monitor-controller/tree/master/dist)
2. Run the exe
3. Add to Windows startup (optional)

## Building from Source
[Instructions here]

## License
MIT

## Credits
Built by William Craig - Forensic engineer who got tired of OSD menus