# 2D Mesh Network-on-Chip (NoC) Router Physical Design (SkyWater 130nm)

[![Process](https://img.shields.io/badge/Process-SkyWater%20130nm%20(sky130)-blue)](https://github.com/google/skywater-pdk)
[![Layout Signoff](https://img.shields.io/badge/Geometric%20DRC-0%20Violations-brightgreen)](reports/drc_report.txt)
[![Frequency](https://img.shields.io/badge/Target%20Clock-100%20MHz%20Budget-emerald)](reports/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

A procedural ASIC Physical Design implementation of a 5-port 2D Mesh Network-on-Chip (NoC) Router targeted for the SkyWater 130nm (`sky130_fd_sc_hd`) layer stack, verified with an automated Python O(N log N) sweep-line geometric DRC engine.

Designed and implemented by **Ly Tuan Nghi ([@lytuannghi](https://github.com/lytuannghi))**.

---

## Technical Specifications

- **Silicon Area:** 380.00 um x 380.00 um (Total Die Area: 0.1444 mm²).
- **Extracted GDSII Structures:** 6 functional macro regions (`L64`), 5,152 active diffusion and polysilicon gate shapes (`L65`/`L66`), 424 Metal 2 tracks (`L70`), 34 VIA3 crossbar bridges (`L73`), and 10 external port regions (`L108`).
- **Switch Architecture:** Central 5-port crossbar core surrounded by symmetrical North, South, East, West, and Local PE buffer regions.
- **Routing Strategy:** Non-overlapping Metal 1/2 local and inter-buffer tracks, Metal 3 horizontal buses, Metal 4 vertical trunks + split H-tree clock arms (routed cleanly around crossbar switches), and Metal 5 power rails.

---

## Physical Verification Summary

| Verification Stage | Method / Tool | Result |
| :--- | :--- | :---: |
| **Geometric DRC** | `scripts/verify_gds_drc.py` (Sweep-line width, spacing, overlap, OOB) | **PASSED (0 Violations)** |
| **Structural Extraction** | Extracted GDSII macro/gate/pin audit (`reports/lvs_report.txt`) | **5,152 gates / 6 macros matched** |
| **Congestion Analysis** | Channel pitch & track allocation check (`reports/congestion_report.txt`) | **Reference Clean (0 Short Tracks)** |

---

## File Structure

```
layout-noc-router/
├── gds/
│   └── noc_router.gds             # Physical GDSII layout stream (1.06 MB, 0 DRC violations)
├── reports/
│   ├── drc_report.txt             # Verified Python sweep-line geometric DRC report
│   ├── lvs_report.txt             # Structural GDSII macro & device inventory report
│   └── congestion_report.txt      # Reference track density analysis report
├── scripts/
│   ├── build_layout_noc_router.py # Procedural layout generator + automatic DRC check
│   └── verify_gds_drc.py          # Standalone binary GDSII sweep-line DRC engine
└── README.md
```

---

## Layout Regeneration & Verification

```bash
python scripts/build_layout_noc_router.py
python scripts/verify_gds_drc.py gds/noc_router.gds --top noc_router_top
klayout gds/noc_router.gds
```
