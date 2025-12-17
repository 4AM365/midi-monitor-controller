1) PyInstaller doesn't like rtmidi

Solution - make a spec file with hidden imports

Edit the new .spec to explicitly include all packages in hiddenimports = []

Then, build from spec. the .spec can also include whether the program is silent or not. pyinstaller MonitorController.spec
