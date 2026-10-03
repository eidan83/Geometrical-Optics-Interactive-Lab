# Changelog

All notable changes to iGOLab (formerly Geometrical Optics Interactive Lab) are documented in this file.

The project follows the principles of Semantic Versioning.

## [2.0.1] - 2026-10-03

### Changed
- Renamed the application to iGOLab (interactive Geometrical Optics Laboratory).
- Preserved the existing website/repository URLs and saved-project format.

### Fixed
- Corrected finite conjugates near the focal distance and synchronized signed focal inputs and lens-type state.
- Preserved the requested thick-lens clear aperture while displaying the curvature-constrained applied aperture.

### Verification
- Added reproducible numerical and browser checks, historical RC1/RC2 snapshots, and a paraxial-versus-exact spherical-refraction benchmark.
- The current named snapshot passed 164 numerical comparisons, 232 focal checks, 12 aperture-state checks and 39 browser cases, plus five emulated viewport profiles.
- The named snapshot has identical inline JavaScript and CSS to the corrected RC2 baseline. New browser results use headless Chromium/Linux; historical author runs use Edge/Windows.

## [2.0.0] - 2026-07-15

### Added

- Interactive simulation of single thin lenses.
- Simulation of two-lens optical systems.
- Lens maker's formula module.
- Interactive concave and convex spherical-mirror simulations.
- Thick-lens simulation and numerical calculations.
- Prism refraction and deviation simulation.
- Parallel-sided glass-slab simulation.
- Interactive optical bench with draggable optical components.
- Dynamic geometrical ray tracing.
- Optical-component rotation controls.
- Measurement tools for distances and angles.
- Guided educational examples.
- Immediate numerical results and visual feedback.
- Responsive browser-based interface.
- Online operation through GitHub Pages.
- Offline operation through the self-contained HTML file.
- Academic citation metadata through `CITATION.cff`.
- GNU General Public License v3.0.

### Improved

- Unified interface across the simulator modules.
- Spherical-mirror ray tracing and educational examples.
- Visualization of optical rays and image formation.
- Layout and use of the available screen area.
- Interactive controls and educational usability.

### Related Research Version

The original version used in the associated educational study remains archived separately as version `v1.0.2`.

DOI: `10.5281/zenodo.18070606`
