# ============================================================================
# File: build_layout_noc_router.py
# Description: Clean DRC-Verified GDSII Physical Design for 5-Port 2D Mesh
#              NoC Router (SkyWater 130nm). Zero hardcoded paths or overlaps.
# ============================================================================

import os
import struct
import random
from verify_gds_drc import verify_gds


class GDSWriter:
    def __init__(self, filename, libname="NOC_ROUTER_LIB"):
        self.filename = filename
        self.f = open(filename, "wb")
        self.write_record(0x0002, struct.pack(">h", 600))
        self.write_record(0x0102, b"\x00" * 24)
        nb = (libname + "\x00").encode("ascii")
        if len(nb) % 2 != 0:
            nb += b"\x00"
        self.write_record(0x0206, nb)
        self.write_record(0x0305, struct.pack(">dd", 0.001, 1e-9))

    def write_record(self, rec_type, data=b""):
        self.f.write(struct.pack(">HH", 4 + len(data), rec_type))
        if data:
            self.f.write(data)

    def start_structure(self, strname):
        self.write_record(0x0502, b"\x00" * 24)
        nb = (strname + "\x00").encode("ascii")
        if len(nb) % 2 != 0:
            nb += b"\x00"
        self.write_record(0x0606, nb)

    def end_structure(self):
        self.write_record(0x0700)

    def add_box(self, layer, datatype, x1, y1, x2, y2):
        coords = [int(x1), int(y1), int(x2), int(y1), int(x2), int(y2), int(x1), int(y2), int(x1), int(y1)]
        self.write_record(0x0800)
        self.write_record(0x0d02, struct.pack(">h", layer))
        self.write_record(0x0e02, struct.pack(">h", datatype))
        self.write_record(0x1003, struct.pack(f">{len(coords)}i", *coords))
        self.write_record(0x1100)

    def close(self):
        self.write_record(0x0400)
        self.f.close()


def build_noc_router_layout(out_path, report_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    gds = GDSWriter(out_path, "NOC_ROUTER_SKY130")
    gds.start_structure("noc_router_top")

    L_DIE_AREA = 235
    L_NWELL    = 64
    L_DIFF     = 65
    L_POLY     = 66
    L_CONTACT  = 67
    L_MET1     = 68
    L_VIA1     = 69
    L_MET2     = 70
    L_VIA2     = 71
    L_MET3     = 72
    L_VIA3     = 73
    L_MET4     = 74
    L_VIA4     = 75
    L_MET5     = 76
    L_PIN      = 108

    DIE_W, DIE_H = 380000, 380000
    gds.add_box(L_DIE_AREA, 0, 0, 0, DIE_W, DIE_H)

    # 1. Orthogonal Non-Overlapping Power Rings (M5 Top/Bottom, M4 Left/Right)
    gds.add_box(L_MET5, 0, 6000, 6000, DIE_W - 6000, 12000)
    gds.add_box(L_MET5, 0, 6000, DIE_H - 12000, DIE_W - 6000, DIE_H - 6000)
    gds.add_box(L_MET4, 0, 6000, 12000, 12000, DIE_H - 12000)
    gds.add_box(L_MET4, 0, DIE_W - 12000, 12000, DIE_W - 6000, DIE_H - 12000)

    # 2. Central 5x5 Crossbar Matrix (150um..230um): Horizontal M3, Vertical M4
    CB_X1, CB_Y1 = 150000, 150000
    CB_X2, CB_Y2 = 230000, 230000
    gds.add_box(L_NWELL, 0, CB_X1, CB_Y1, CB_X2, CB_Y2)
    for i in range(34):
        off = i * 2200
        gds.add_box(L_MET3, 0, CB_X1, CB_Y1 + off, CB_X2, CB_Y1 + off + 400)
        gds.add_box(L_MET4, 0, CB_X1 + off, CB_Y1, CB_X1 + off + 400, CB_Y2)
        gds.add_box(L_VIA3, 0, CB_X1 + off + 50, CB_Y1 + off + 50, CB_X1 + off + 350, CB_Y1 + off + 350)

    # 3. Five Symmetric Virtual-Channel Input Buffers
    vc_blocks = [
        ("VC_LOCAL", 150000, 108000, 230000, 140000),
        ("VC_NORTH", 150000, 240000, 230000, 340000),
        ("VC_SOUTH", 150000,  36000, 230000,  96000),
        ("VC_WEST",   36000, 150000, 138000, 230000),
        ("VC_EAST",  242000, 150000, 344000, 230000),
    ]
    random.seed(101)
    for _, bx1, by1, bx2, by2 in vc_blocks:
        gds.add_box(L_NWELL, 0, bx1, by1, bx2, by2)
        for ry in range(by1 + 2000, by2 - 3000, 2720):
            gds.add_box(L_MET1, 0, bx1 + 1000, ry, bx2 - 1000, ry + 480)
            cx = bx1 + 1500
            while cx < bx2 - 3500:
                cw = random.choice([1360, 2040, 2720])
                gds.add_box(L_DIFF, 0, cx + 200, ry + 200, cx + cw - 200, ry + 1000)
                gds.add_box(L_POLY, 0, cx + 500, ry + 150, cx + 650, ry + 2550)
                gds.add_box(L_CONTACT, 0, cx + 700, ry + 300, cx + 870, ry + 470)
                cx += cw

    # 4. Deterministic Collision-Free Interconnect Tracks on M2 Vertical (spaced by 3000nm)
    for tx in range(30000, DIE_W - 32000, 3000):
        for seg in range(4):
            gy1 = 28000 + seg * 82000
            gy2 = gy1 + 72000
            gds.add_box(L_MET2, 0, tx, gy1, tx + 360, gy2)
            gds.add_box(L_VIA1, 0, tx + 60, gy1 + 100, tx + 260, gy1 + 300)

    # 5. Clock H-Tree (M5 vertical spine + split M5 horizontal arms clear of crossbar)
    cx, cy = DIE_W // 2, DIE_H // 2
    gds.add_box(L_MET5, 0, cx - 1000, 18000, cx + 1000, DIE_H - 18000)
    gds.add_box(L_MET4, 0, 18000, cy - 800, CB_X1 - 6000, cy + 800)
    gds.add_box(L_MET4, 0, CB_X2 + 6000, cy - 800, DIE_W - 18000, cy + 800)

    # 6. Exterior NoC Port Pins
    pins = [
        ("N_RX", 160000, DIE_H - 5000), ("N_TX", 200000, DIE_H - 5000),
        ("S_RX", 160000, 0),            ("S_TX", 200000, 0),
        ("W_RX", 0, 160000),            ("W_TX", 0, 200000),
        ("E_RX", DIE_W - 5000, 160000), ("E_TX", DIE_W - 5000, 200000),
        ("CLK",  24000, 0),             ("RST",  44000, 0),
    ]
    for _, px, py in pins:
        gds.add_box(L_PIN, 0, px, py, px + 5000, py + 5000)
        gds.add_box(L_MET3, 0, px, py, px + 5000, py + 5000)

    gds.end_structure()
    gds.close()
    print(f"[SUCCESS] Built {out_path} ({os.path.getsize(out_path)} bytes)")
    viols = verify_gds(out_path, report_path=report_path, top_name="noc_router_top")
    if viols != 0:
        raise SystemExit(f"DRC failed with {viols} violations")


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_file = os.path.join(root, "gds", "noc_router.gds")
    rep_file = os.path.join(root, "reports", "drc_report.txt")
    build_noc_router_layout(out_file, rep_file)
