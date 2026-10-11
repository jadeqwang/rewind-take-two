#!/usr/bin/env python3
"""Dump frame(s) of a video with a 100-px design grid for picking corner-pin points: frame.py VIDEO OUT.jpg [t_sec] [crop x0,y0,x1,y1]"""
import sys
import cv2
v, out = sys.argv[1], sys.argv[2]
t = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
cap = cv2.VideoCapture(v); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read()
f = cv2.resize(f, (1920, 1080))
for x in range(0, 1920, 100):
    cv2.line(f, (x, 0), (x, 1079), (0, 0, 255) if x % 500 == 0 else (0, 140, 255), 1)
    cv2.putText(f, str(x), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
for y in range(0, 1080, 100):
    cv2.line(f, (0, y), (1919, y), (0, 0, 255) if y % 500 == 0 else (0, 140, 255), 1)
    cv2.putText(f, str(y), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
if len(sys.argv) > 4:
    x0, y0, x1, y1 = map(int, sys.argv[4].split(","))
    f = f[y0:y1, x0:x1]
cv2.imwrite(out, f)
