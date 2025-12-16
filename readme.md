This repo is used to figure out my monitor settings on a BenQ Mobiuz EX321UX.

These are the options:
- Local dimming
- Crosshair
- Automatic brightness
- Manual brightness setting

Communication from computer to monitor is done with the usb-b upstream port using the DDC/CI protocol. I'll use a program like ControlMyMonitor to run it.

BenQ has custom functions beyond the usual DDC/CI stuff. These are called VCPs. Let's find them out with this command:

''' ControlMyMonitor.exe /smonitor "BenQ EX321UX" /SaveReport "report.txt"

For CAD and work (photo review), we want true to life settings. Some people say local dimming is distracting here.

For entertainment, we definitely want local dimming.

BI+ is fine, but locks some things out. It can also compete with other algos and disable certain settings.

We can either have different profiles, or break the controls out.

If we use a Behringer X-Touch Mini, we can use a knob for brightness, a knob for night mode (reduce blue channel), a button for local dimming, and a button for crosshair. That would be cool!

HDR is a cool feature too. Most content is mastered for standard dynamic range, and for work I definitely want standard. I want to see what's really going on. We might want to apply HDR on top of a game or video. Let's make that a button.


 It sounds like my best approach will be this: I'll discover the VPC codes and then have a python layer between the computer and a DDC program. The python layer will assign a button on the x-touch mini to HDR, local dimming, and crosshair. A knob will go to brightness and a knob will go to 'night mode' e.g. cut the blue tones out.

 https://www.nirsoft.net/utils/control_my_monitor.html