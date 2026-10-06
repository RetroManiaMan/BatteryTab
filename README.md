# BatteryTab
ClockTab but for viewing your battery status. Your battery percentage, live in the page *and* in the tab icon.

## Chrome, Edge, Brave, Opera
Just open `index.html` (or your hosted copy) and pin the tab. Nothing else needed.

## Firefox and Safari
These browsers don't let websites read your battery, so BatteryTab uses a tiny helper:

```
python3 batterytab-helper.py
```

Keep it running and the page connects on its own (macOS, Linux and Windows; Python 3, no installs).
Add `--origin https://your-site` to only allow your own site to read it. Your browser may ask
permission to access the local network the first time: click Allow.
