[README.md](https://github.com/user-attachments/files/33129510/README.md)
# BatteryTab
ClockTab but for viewing your battery status. Your battery percentage, live in the page *and* in the tab icon.

## How it works
- **Chrome, Edge, Brave, Opera:** BatteryTab reads the browser's Battery API. Chrome only delivers readings
  while the tab is visible, so the icon freezes while you're on another tab and catches up when you return.
- **Always-on tracking (any browser):** run the helper. It reads your battery from the OS, so the tab icon keeps
  updating even when the tab is in the background.
- **Firefox and Safari:** they have no battery API, so the helper is required.

## The helper
```
python3 batterytab-helper.py
```
Works on macOS, Linux and Windows (Python 3, nothing to install). Keep it running.
- Firefox/Safari connect automatically. In Chrome, tap **Connect to helper** once.
- Add `--origin https://your-site` to only allow your own site to read it.
- Your browser may ask for local network permission the first time: click Allow.
