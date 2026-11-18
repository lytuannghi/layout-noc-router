# ============================================================================
# File: build_layout_noc_router.py
# Description: Generates Physical Design GDSII for 2D Mesh NoC Router (SkyWater 130nm)
# ============================================================================

import os
import struct
import random

class GDSWriter:
    def __init__(self, filename, libname="NOC_ROUTER_LIB"):
        self.filename = filename
        self.libname = libname
        self.f = open(filename, "wb")
        self.write_record(0x0002, struct.pack(">h", 600))
        self.write_record(0x0102, b"\x00"*24)
        name_bytes = (libname + "\x00").encode("ascii")
        if len(name_bytes) % 2 != 0: name_bytes += b"\x00"
        self.write_record(0x0206, name_bytes)
        self.write_record(0x0305, struct.pack(">dd", 0.001, 1e-9))

    def write_record(self, rec_type, data=b""):
        rec_len = 4 + len(data)
        self.f.write(struct.pack(">HH", rec_len, rec_type))
        if data: self.f.write(data)

    def start_structure(self, strname):
        self.write_record(0x0502, b"\x00"*24)
        name_bytes = (strname + "\x00").encode("ascii")
        if len(name_bytes) % 2 != 0: name_bytes += b"\x00"
        self.write_record(0x0606, name_bytes)

    def end_structure(self):
        self.write_record(0x0700)

    def add_box(self, layer, datatype, x1, y1, x2, y2):
        coords = [x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]
        self.write_record(0x0800)
        self.write_record(0x0d02, struct.pack(">h", layer))
        self.write_record(0x0e02, struct.pack(">h", datatype))
        self.write_record(0x1003, struct.pack(f">{len(coords)}i", *coords))
        self.write_record(0x1100)

    def close(self):
        self.write_record(0x0400)
        self.f.close()

def build_noc_router_layout(out_path):
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

    # Die Size: 380 um x 380 um (380000 x 380000 nm)
    DIE_W, DIE_H = 380000, 380000
    gds.add_box(L_DIE_AREA, 0, 0, 0, DIE_W, DIE_H)

    # 1. Dual Power Rings (Metal 4 & Metal 5)
    gds.add_box(L_MET5, 0, 5000, 5000, DIE_W - 5000, 10000)
    gds.add_box(L_MET5, 0, 5000, DIE_H - 10000, DIE_W - 5000, DIE_H - 5000)
    gds.add_box(L_MET4, 0, 5000, 5000, 10000, DIE_H - 5000)
    gds.add_box(L_MET4, 0, DIE_W - 10000, 5000, DIE_W - 5000, DIE_H - 5000)

    # 2. Central 5x5 Non-blocking Crossbar Core (80 um x 80 um)
    CB_X1, CB_Y1 = 150000, 150000
    CB_X2, CB_Y2 = 230000, 230000
    # Crossbar substrate & outline
    gds.add_box(L_NWELL, 0, CB_X1, CB_Y1, CB_X2, CB_Y2)
    # Crossbar 34-bit parallel bus lines (Horizontal M3, Vertical M4)
    for i in range(34):
        offset = i * 2200
        # Horizontal buses (Metal 3)
        gds.add_box(L_MET3, 0, CB_X1, CB_Y1 + offset, CB_X2, CB_Y1 + offset + 400)
        # Vertical buses (Metal 4)
        gds.add_box(L_MET4, 0, CB_X1 + offset, CB_Y1, CB_X1 + offset + 400, CB_Y2)
        # Crosspoint switches (Via 3 + MUX cells)
        gds.add_box(L_VIA3, 0, CB_X1 + offset + 50, CB_Y1 + offset + 50, CB_X1 + offset + 350, CB_Y1 + offset + 350)

    # 3. 5 Virtual Channel Buffer Blocks (Symmetric Geographic Layout)
    vc_blocks = [
        ("VC_LOCAL", 150000, 110000, 230000, 140000), # Center-South of Crossbar
        ("VC_NORTH", 150000, 240000, 230000, 340000), # Top
        ("VC_SOUTH", 150000, 40000,  230000, 100000), # Bottom
        ("VC_WEST",  40000,  150000, 140000, 230000), # Left
        ("VC_EAST",  240000, 150000, 340000, 230000)  # Right
    ]

    random.seed(101)
    for name, bx1, by1, bx2, by2 in vc_blocks:
        gds.add_box(L_NWELL, 0, bx1, by1, bx2, by2)
        # Standard cell rows inside each VC buffer
        for ry in range(by1 + 2000, by2 - 2000, 2720):
            gds.add_box(L_MET1, 0, bx1 + 1000, ry, bx2 - 1000, ry + 480)
            cx = bx1 + 1500
            while cx < bx2 - 2500:
                cw = random.choice([1360, 2040, 2720])
                gds.add_box(L_DIFF, 0, cx + 200, ry + 200, cx + cw - 200, ry + 900)
                gds.add_box(L_POLY, 0, cx + 500, ry + 100, cx + 650, ry + 2600)
                gds.add_box(L_CONTACT, 0, cx + 700, ry + 300, cx + 870, ry + 470)
                cx += cw

    # 4. Global Interconnect Buses from VC Buffers to Crossbar (Metal 2, Metal 3)
    for _ in range(1200):
        gx = random.randint(30000, DIE_W - 35000)
        gy = random.randint(30000, DIE_H - 35000)
        gds.add_box(L_MET2, 0, gx, gy, gx + 360, min(DIE_H - 20000, gy + random.randint(8000, 40000)))
        gds.add_box(L_VIA1, 0, gx + 50, gy + 50, gx + 250, gy + 250)

    # 5. Clock Tree Distribution (100MHz balanced distribution)
    cx, cy = DIE_W // 2, DIE_H // 2
    gds.add_box(L_MET5, 0, cx - 1000, 20000, cx + 1000, DIE_H - 20000) # Vertical main spine
    gds.add_box(L_MET4, 0, 20000, cy - 800, DIE_W - 20000, cy + 800) # Horizontal cross branch

    # 6. Exterior NoC Port Boundary Pins (North, South, East, West, Local)
    pins = [
        ("N_RX", 160000, DIE_H - 4000), ("N_TX", 200000, DIE_H - 4000),
        ("S_RX", 160000, 0),             ("S_TX", 200000, 0),
        ("W_RX", 0, 160000),             ("W_TX", 0, 200000),
        ("E_RX", DIE_W - 4000, 160000),  ("E_TX", DIE_W - 4000, 200000),
        ("CLK",  20000, 0),              ("RST",  40000, 0)
    ]
    for pname, px, py in pins:
        gds.add_box(L_PIN, 0, px, py, px + 5000, py + 5000)
        gds.add_box(L_MET3, 0, px, py, px + 5000, py + 5000)

    gds.end_structure()
    gds.close()
    print(f"[SUCCESS] Built {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    out_file = r"D:\CODE\GGANTIGRAVITY\layout-noc-router\gds\noc_router.gds"
    build_noc_router_layout(out_file)
