# iGOLab

**interactive Geometrical Optics Laboratory** — formerly Geometrical Optics Interactive Lab.

A free, self-contained browser application for geometrical-optics calculations and configurable optical-system construction.

## Open the simulator

[Launch iGOLab](https://eidan83.github.io/Geometrical-Optics-Interactive-Lab/), or download this repository and open `index.html` locally. No installation is required. Existing saved projects remain compatible.

## Modules and tools

- Single thin lens, two thin lenses and lens maker's formula.
- Spherical mirrors, paraxial thick lenses, prisms and parallel-sided slabs.
- Editable optical bench with sources, optical elements, screens and detectors.
- Dragging and rotation, guided examples, rulers and protractors.
- Project export/import, undo/redo and PNG export.

## Project history

This software was first archived as Geometrical Optics Interactive Lab v2.0.0 on **15 July 2026** ([original archive](https://doi.org/10.5281/zenodo.21370215)). The iGOLab name continues the same project; the original archive and development history remain available.

## Version 2.0.1

This release adopts the iGOLab name and includes corrections to near-focal calculations, signed focal inputs and requested/applied thick-lens aperture handling. See [CHANGELOG.md](CHANGELOG.md).

The released `index.html` is byte-identical to `verification/software_igolab/index.html` (SHA256 `95fa9222b334bb3b80ee67ac36d88d200ae995a95b252f11bd0336286d7c829c`). Its inline JavaScript and CSS are identical to the corrected RC2 baseline.

## Verification and model limits

The current snapshot passed 164 numerical comparisons, 232 focal checks, 12 aperture-state checks and 39 browser cases, plus five emulated viewport profiles. The current browser run used headless Chromium 134 on Linux. Earlier Edge/Windows results and their exact RC1/RC2 sources are retained separately in `verification/`.

Run the numerical checks with Node.js:

```sh
cd verification/software_igolab
node run_numeric.cjs
node test_focal_numeric.cjs
node test_aperture.cjs
```

Browser-test instructions and requirements accompany the scripts. `verification/validation/` contains the paraxial-versus-exact spherical-refraction benchmark and an independent RayOptics comparison.

The analytical lens modules use first-order/paraxial models. The bench's thick-lens boundary is segmented; the smooth-surface benchmark is not a convergence proof for that representation. Detector outputs are relative model estimates. These technical checks do not establish learning gains or educational effectiveness.

## Citation and archive

Eidan A. Abdullah, *iGOLab (interactive Geometrical Optics Laboratory)*, version 2.0.1 (2026).

[Zenodo record covering all versions](https://doi.org/10.5281/zenodo.21370214). The all-versions DOI is used in `CITATION.cff`; the earlier version 2.0.0 remains archived at [10.5281/zenodo.21370215](https://doi.org/10.5281/zenodo.21370215).

The earlier educational research simulator (v1.0.2) is a separate, smaller platform archived at [10.5281/zenodo.18070606](https://doi.org/10.5281/zenodo.18070606).

## Author and license

Eidan A. Abdullah — Department of Physics, College of Science, Wasit University, Iraq. [ORCID](https://orcid.org/0009-0009-4103-2360).

GNU General Public License v3.0 only; see [LICENSE](LICENSE).
