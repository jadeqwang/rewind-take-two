"""v6 (Jade, 2:13: "there are a few frames where a larger agent's head is visible"): ORANGE's matte in c2/take_1
(c2t1_L, level.py) keeps any agent that touches her within 281 px of her colour, so on take frames 17-28 and 37-38
the take's own leading agent (head, shoulder, arm and hands, at the take's scale, twice the size of the agents layer)
is drawn with her in C2a (visible at 132.708-133.042 and 133.333).  This erases him with hand-keyed polygons
(source px, per take frame; her rear sneaker, which the agent grabs, is kept) and writes c2t1_Lc.mp4, the matte the
co-op level uses for ORANGE in C2a and C2b.  Frames 106-108 (C2b) lose the take's flat pencil point (see below).
All other frames are c2t1_L unchanged.
    tools/engrave/.venv/bin/python tools/v4B/coop/unleak.py"""
import os
import subprocess

import cv2
import numpy as np

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop"
FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")

ERASE = {   # take frame: polygon (source px, 1920x1080) holding the agent's parts of the matte
    17: [(550, 265), (720, 265), (810, 360), (812, 397), (790, 412), (700, 416), (697, 452), (550, 452)],
    18: [(550, 262), (700, 262), (810, 350), (812, 397), (790, 412), (700, 416), (697, 452), (550, 452)],
    19: [(550, 280), (758, 280), (762, 340), (800, 405), (800, 418), (778, 430), (775, 520), (550, 520)],
    20: [(550, 290), (780, 290), (795, 410), (802, 440), (800, 540), (550, 540)],
    21: [(550, 330), (840, 330), (845, 440), (870, 560), (880, 620), (550, 620)],
    22: [(550, 330), (830, 330), (835, 420), (850, 445), (845, 555), (870, 560), (870, 585), (550, 585)],
    24: [(550, 340), (890, 340), (900, 450), (915, 550), (945, 570), (945, 640), (550, 640)],
    25: [(550, 350), (935, 350), (940, 530), (948, 640), (550, 640)],
    26: [(550, 350), (920, 350), (935, 470), (940, 640), (550, 640)],
    28: [(550, 350), (948, 350), (948, 640), (550, 640)],
    37: [(1000, 440), (1150, 440), (1170, 520), (1180, 600), (1200, 660), (1000, 660)],
    38: [(1000, 440), (1160, 440), (1172, 520), (1178, 600), (1195, 660), (1000, 660)],
    # v6 (Jade, 2:13-14: "part of the tip of the pencil is detached and visible"): in C2b the bridge is raised from
    # 134.20, but the take's pencil still lies flat and its point, touching her heel, is in her matte on take frames
    # 106-108 (134.417-134.500)
    106: [(1300, 595), (1405, 595), (1428, 628), (1405, 665), (1300, 665)],
    107: [(1300, 595), (1405, 595), (1428, 628), (1405, 665), (1300, 665)],
    108: [(1385, 612), (1440, 612), (1440, 652), (1385, 652)],
}


def main():
    enc = None
    i = 0
    while os.path.exists(f"{D}/c2t1_L/{i:05d}.png"):
        g = cv2.imread(f"{D}/c2t1_L/{i:05d}.png", 0)
        if i in ERASE:
            cv2.fillPoly(g, [np.array(ERASE[i], np.int32)], 0)
        if enc is None:
            h, w = g.shape
            enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{w}x{h}", "-r", "24",
                                    "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", f"{D}/c2t1_Lc.mp4"],
                                   stdin=subprocess.PIPE)
        enc.stdin.write(g.tobytes())
        i += 1
    enc.stdin.close()
    enc.wait()
    print("c2t1_Lc.mp4:", i, "frames;", len(ERASE), "cleaned")


if __name__ == "__main__":
    main()
