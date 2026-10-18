#!/usr/bin/env python3
"""ScreenBridge 图标候选生成 v12 —— 三个方向任选。

A「光环头像」：白色安卓机器人头像特写（半圆头+天线+眼睛微笑+圆肩），
   身后一枚细红鸿蒙环光环 —— 头像大、环退后，现代 app 感
B「徽章嵌图」：红色鸿蒙环为主徽章（粗环+柔光），环内嵌白色安卓机器人头像 ——
   鸿蒙为主导框架，安卓嵌其中，品牌结合最直接
C「圆润吉祥物」：白色完整机器人（头身腿一体）+眼睛微笑，身后半透明红环 ——
   完整形象 + 友好吉祥物气质，大众市场向

共同基础：蓝紫对角渐变底、红=鸿蒙、白=安卓。
"""
from PIL import Image, ImageDraw, ImageFilter

S = 4096
OUT = 1024
cx, cy = S // 2, S // 2

def I(x):
    return int(round(x))

def gradient_bg():
    img = Image.new("RGB", (S, S), (0x3B, 0x82, 0xF6))
    px = img.load()
    TL = (0x4F, 0x8E, 0xFF); TR = (0x3B, 0x82, 0xF6)
    BL = (0x63, 0x63, 0xF1); BR = (0x8B, 0x5C, 0xF6)
    for y in range(S):
        for x in range(S):
            tx = x / (S - 1); ty = y / (S - 1)
            top = tuple(TL[i] + (TR[i] - TL[i]) * tx for i in range(3))
            bot = tuple(BL[i] + (BR[i] - BL[i]) * tx for i in range(3))
            col = tuple(int(top[i] + (bot[i] - top[i]) * ty) for i in range(3))
            px[x, y] = col
    return img.convert("RGBA")

def red_halo(dr, cx, cy, r, width, alpha, blur):
    """在图层上叠加柔光红环（半透明）。"""
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(0xE6, 0x00, 0x12, alpha), width=width)
    halo = halo.filter(ImageFilter.GaussianBlur(blur))
    dr._image.paste(halo, (0, 0), halo)

def red_ring(dr, cx, cy, r, width, alpha):
    dr.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(0xE6, 0x00, 0x12, alpha), width=width)

def white_head(dr, cx, cy_top, r, ant_len, ant_r, ant_spread, eyes_y, mouth_y):
    """半圆头（弦在 cy_top）+ 天线 + 眼睛微笑。cy_top=弦 y 坐标。"""
    WHITE = (255, 255, 255, 255)
    INK = (0x14, 0x24, 0x3C, 255)
    head_cy = cy_top  # 圆心=弦 y
    dr.chord([cx-r, head_cy-r, cx+r, head_cy+r], 180, 360, fill=WHITE)
    top_y = head_cy - r
    for side in (-1, 1):
        ex = cx + side * ant_spread
        ey = top_y - ant_len
        dr.line([cx, top_y, ex, ey], fill=WHITE, width=I(S*0.012))
        dr.ellipse([ex-ant_r, ey-ant_r, ex+ant_r, ey+ant_r], fill=WHITE)
    # 眼睛
    eye_r = I(S * 0.014)
    for exx in (cx - I(S*0.052), cx + I(S*0.052)):
        dr.ellipse([exx-eye_r, eyes_y-eye_r, exx+eye_r, eyes_y+eye_r], fill=INK)
    # 微笑
    mw = I(S * 0.040)
    dr.arc([cx-mw, mouth_y-I(S*0.012), cx+mw, mouth_y+I(S*0.030)],
           20, 160, fill=INK, width=I(S*0.012))

def save(img, path):
    img.convert("RGB").resize((OUT, OUT), Image.LANCZOS).save(path)
    print("saved", path)

# ============ A「光环头像」 ============
img = gradient_bg()
dr = ImageDraw.Draw(img, "RGBA")
# 肩（圆角矩形，顶边与头弦重合）
body_w, body_h = I(S*0.30), I(S*0.17)
body_y0 = I(S*0.47)
dr.rounded_rectangle([cx-body_w//2, body_y0, cx+body_w//2, body_y0+body_h],
                     radius=I(S*0.055), fill=(255, 255, 255, 255))
white_head(dr, cx, body_y0, I(S*0.19), I(S*0.062), I(S*0.015), I(S*0.055),
           I(S*0.385), I(S*0.425))
# 身后红环（细柔）
red_halo(dr, cx, S//2, I(S*0.415), I(S*0.026), 120, I(S*0.022))
red_ring(dr, cx, S//2, I(S*0.415), I(S*0.008), 200)
save(img, "/Users/apple/projects/screen-bridge/assets/candidates/icon_A.png")

# ============ B「徽章嵌图」 ============
img = gradient_bg()
dr = ImageDraw.Draw(img, "RGBA")
# 红环徽章（粗+柔光）
red_halo(dr, cx, S//2, I(S*0.345), I(S*0.030), 140, I(S*0.020))
red_ring(dr, cx, S//2, I(S*0.345), I(S*0.014), 230)
# 环内头像（弦 y 略低于环心，头居中偏上）
white_head(dr, cx, I(S*0.545), I(S*0.165), I(S*0.052), I(S*0.013), I(S*0.048),
           I(S*0.475), I(S*0.505))
save(img, "/Users/apple/projects/screen-bridge/assets/candidates/icon_B.png")

# ============ C「圆润吉祥物」 ============
img = gradient_bg()
dr = ImageDraw.Draw(img, "RGBA")
# 背景淡红环
red_halo(dr, cx, S//2, I(S*0.430), I(S*0.024), 90, I(S*0.024))
red_ring(dr, cx, S//2, I(S*0.430), I(S*0.007), 150)
# 完整机器人（一体剪影）
WHITE = (255, 255, 255, 255)
INK = (0x14, 0x24, 0x3C, 255)
body_w, body_h = I(S*0.245), I(S*0.205)
body_x0, body_y0 = cx-body_w//2, I(S*0.420)
body_r = I(S*0.060)
# 腿
leg_w, leg_h = I(S*0.050), I(S*0.076)
leg_y0 = body_y0 + body_h
for lx in (cx - I(S*0.046), cx + I(S*0.046)):
    dr.rounded_rectangle([lx-leg_w//2, leg_y0, lx+leg_w//2, leg_y0+leg_h],
                         radius=leg_w//2, fill=WHITE)
# 身体
dr.rounded_rectangle([body_x0, body_y0, body_x0+body_w, body_y0+body_h],
                     radius=body_r, fill=WHITE)
# 头（chord，底边=身体顶边）
head_r = I(S*0.100)
head_cy = body_y0
dr.chord([cx-head_r, head_cy-head_r, cx+head_r, head_cy+head_r], 180, 360, fill=WHITE)
# 天线
ant_len = I(S*0.056); ant_r = I(S*0.015)
top_y = head_cy - head_r
for side in (-1, 1):
    ex = cx + side * I(S*0.050); ey = top_y - ant_len
    dr.line([cx, top_y, ex, ey], fill=WHITE, width=I(S*0.011))
    dr.ellipse([ex-ant_r, ey-ant_r, ex+ant_r, ey+ant_r], fill=WHITE)
# 眼睛（头部）
eye_r = I(S*0.013)
for exx in (cx - I(S*0.048), cx + I(S*0.048)):
    dr.ellipse([exx-eye_r, I(S*0.348)-eye_r, exx+eye_r, I(S*0.348)+eye_r], fill=INK)
# 微笑（头部下方）
mw = I(S*0.036)
dr.arc([cx-mw, I(S*0.376)-I(S*0.010), cx+mw, I(S*0.376)+I(S*0.026)],
       20, 160, fill=INK, width=I(S*0.011))
save(img, "/Users/apple/projects/screen-bridge/assets/candidates/icon_C.png")
