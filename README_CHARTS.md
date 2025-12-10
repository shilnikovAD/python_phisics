# Period Analysis Charts

The pendulum simulation includes period analysis charts that show:
1. **Period vs Amplitude**: How the oscillation period depends on the initial amplitude (for undamped oscillations)
2. **Period vs Damping**: How the oscillation period changes with different damping coefficients

## Chart.js Requirement

The charts use Chart.js library loaded from CDN. If you're running the application in an environment with ad blockers or restricted internet access, the charts may not display. The application will gracefully handle this and show a console warning.

To use the charts:
- Ensure Chart.js can be loaded from: https://cdn.jsdelivr.net/npm/chart.js
- Or download Chart.js manually and update the script tag in index.html to point to a local copy

The rest of the application (pendulum simulation, energy monitoring, etc.) works independently of the charts.
