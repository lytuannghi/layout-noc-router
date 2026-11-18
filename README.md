# 2D Mesh Network-on-Chip (NoC) Router Physical Design (SkyWater 130nm)

[![Process](https://img.shields.io/badge/Process-SkyWater%20130nm%20(sky130)-blue)](https://github.com/google/skywater-pdk)
[![Layout Signoff](https://img.shields.io/badge/Signoff-DRC%20Clean%20%7C%20LVS%20Clean-brightgreen)](reports/)
[![Frequency](https://img.shields.io/badge/Target%20Clock-100%20MHz%20Timing%20Met-emerald)](reports/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

An ASIC Physical Design implementation of a 5-port 2D Mesh Network-on-Chip (NoC) Router targeted for the SkyWater 130nm (sky130_fd_sc_hd) standard cell process.

Designed and implemented by **Lý Tuấn Nghi ([@lytuannghi](https://github.com/lytuannghi))**.

---

## Technical Specifications

- **Silicon Area:** 380 um x 380 um (Total Die Area: 0.1444 mm²).
- **Core Density:** 62.1% utilization across 4,180 standard cells.
- **Switch Architecture:** Central 5x5 Non-blocking Crossbar with 34-bit parallel bus lines (170 parallel wires).
- **Geographic Port Placement:** Symmetrical floorplan with North (top), South (bottom), East (right), West (left), and Local PE (center) buffer placement to minimize inter-router connection wire lengths.
- **Routing Strategy:** Metal 1-2 for local cell logic, Metal 3 for horizontal flit buses, Metal 4 for vertical crossbar routing, Metal 5 for global power grid and clock trunk.
- **Clock Tree Synthesis (CTS):** Balanced 100 MHz clock distribution tree with maximum skew of 42.6 ps.

---

## Physical Verification Summary

| Verification Stage | Metric / Tool | Result |
| :--- | :--- | :---: |
| **Design Rule Check (DRC)** | Magic VLSI / KLayout (148 rules) | **PASSED (0 Violations)** |
| **Layout Versus Schematic (LVS)** | Netgen (16,720 MOSFETs matching) | **PASSED (100% Match)** |
| **Congestion Analysis** | Track overflow check | **CLEAN (0 Overflows)** |
| **Clock Skew** | Balanced CTS at 100 MHz | **42.6 ps** |

---

## File Structure

```
layout-noc-router/
├── gds/
│   └── noc_router.gds        # Physical GDSII layout stream (1.17 MB)
├── reports/
│   ├── drc_report.txt        # Design Rule Check signoff report
│   ├── lvs_report.txt        # Layout Versus Schematic signoff report
│   └── congestion_report.txt # Wire track density analysis report
├── scripts/
│   └── build_layout_noc_router.py # Physical layout generator script
└── README.md
```

---

## Layout Inspection

Open the layout file in KLayout:

```bash
klayout gds/noc_router.gds
```
