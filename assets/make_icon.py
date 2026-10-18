#!/usr/bin/env python3
"""ScreenBridge 图标 v16 —— 成熟投屏 Logo（标准投屏符号化）
设计语言：
- 主体 = 全球通用「屏幕镜像」符号（圆角屏幕 + 底部三角），一眼即知"投屏"
- 屏幕内安卓绿圆点 = 被投屏的安卓设备
- 屏幕顶鸿蒙红信号弧 = 鸿蒙互联（克制点缀）
- 深蓝紫渐变底 + 屏幕微渐变（白→浅蓝白）提升产品质感，告别吉祥物与拼凑感
"""
from PIL import Image, ImageDraw, ImageFilter

S = 4096
OUT = 1024
cx, cy = S // 2, S // 2

def I(x):
    return int(round(x))

# ---- 深蓝紫对角渐变背景 ----
small = Image.new("RGB", (4, 4))
TL = (0x26, 0x36, 0x5E); TR = (0x1B, 0x29, 0x4B)
BL = (0x33, 0x2B, 0x6E); BR = (0x16, 0x1B, 0x3A)
small.putpixel((0, 0), TL); small.putpixel((3, 0), TR)
small.putpixel((0, 3), BL); small.putpixel((3, 3), BR)
img = small.resize((S, S), Image.BICUBIC).convert("RGBA")

# 中央柔光
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([cx - I(S * 0.36), cy - I(S * 0.36),
            cx + I(S * 0.36), cy + I(S * 0.36)],
           fill=(130, 165, 255, 46))
glow = glow.filter(ImageFilter.GaussianBlur(I(S * 0.14)))
img = Image.alpha_composite(img, glow)

# ---- 屏幕符号（白色→浅蓝白 垂直渐变，带投影）----
sw, sh = I(S * 0.300), I(S * 0.330)
scy = I(cy + S * 0.012)
sx0, sy0 = cx - sw // 2, scy - sh // 2
radius = I(S * 0.085)

# 投影
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([sx0, sy0 + I(S * 0.022),
                      sx0 + sw, sy0 + sh + I(S * 0.022)],
                     radius=radius, fill=(0, 0, 0, 95))
shadow = shadow.filter(ImageFilter.GaussianBlur(I(S * 0.048)))
img = Image.alpha_composite(img, shadow)

# 屏幕渐变填充
screen = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd2 = ImageDraw.Draw(screen)
sd2.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh],
                      radius=radius, fill=(255, 255, 255, 255))
mask = screen.split()[3]
W_TOP = (255, 255, 255); W_BOT = (226, 233, 249)
for y in range(S):
    t = y / (S - 1)
    c = tuple(int(W_TOP[i] + (W_BOT[i] - W_TOP[i]) * t) for i in range(3))
    row = Image.new("RGBA", (S, 1), c + (255,))
    screen.paste(row, (0, y), mask.crop((0, y, S, y + 1)))
img = Image.alpha_composite(img, screen)
dr = ImageDraw.Draw(img, "RGBA")

# ---- 底部三角（屏幕镜像符号，顶点朝上伸入屏幕）----
tb = sy0 + sh + I(S * 0.050)          # 三角底边（屏幕外下方）
tv = sy0 + sh - I(S * 0.040)          # 三角顶点（伸入屏幕内）
thw = I(S * 0.075)                     # 半底宽
tri = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(tri)
td.polygon([(cx - thw, tb), (cx + thw, tb), (cx, tv)],
           fill=(255, 255, 255, 255))
tmask = tri.split()[3]
for y in range(S):
    t = y / (S - 1)
    c = tuple(int(W_TOP[i] + (W_BOT[i] - W_TOP[i]) * t) for i in range(3))
    row = Image.new("RGBA", (S, 1), c + (255,))
    tri.paste(row, (0, y), tmask.crop((0, y, S, y + 1)))
img = Image.alpha_composite(img, tri)
dr = ImageDraw.Draw(img, "RGBA")

# ---- 安卓绿圆点（屏内）----
d_r = I(S * 0.028)
dcx, dcy = cx, I(scy - S * 0.030)
dglow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
dd = ImageDraw.Draw(dglow)
dd.ellipse([dcx - I(d_r * 2.5), dcy - I(d_r * 2.5),
            dcx + I(d_r * 2.5), dcy + I(d_r * 2.5)],
           fill=(0x3D, 0xDC, 0x84, 55))
dglow = dglow.filter(ImageFilter.GaussianBlur(I(S * 0.028)))
img = Image.alpha_composite(img, dglow)
dr = ImageDraw.Draw(img, "RGBA")
dr.ellipse([dcx - d_r, dcy - d_r, dcx + d_r, dcy + d_r],
           fill=(0x3D, 0xDC, 0x84, 255))

# ---- 鸿蒙红信号弧（两条，从屏幕后部向上发出）----
RED = (0xE6, 0x00, 0x12)
arc_cy = I(scy - S * 0.120)
A0, A1 = 198, 342

halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
for rr, ww in ((I(S * 0.148), I(S * 0.030)), (I(S * 0.088), I(S * 0.030))):
    hd.arc([cx - rr, arc_cy - rr, cx + rr, arc_cy + rr],
           A0, A1, fill=RED + (50,), width=ww)
halo = halo.filter(ImageFilter.GaussianBlur(I(S * 0.018)))
img = Image.alpha_composite(img, halo)
dr = ImageDraw.Draw(img, "RGBA")

for rr in (I(S * 0.148), I(S * 0.088)):
    dr.arc([cx - rr, arc_cy - rr, cx + rr, arc_cy + rr],
           A0, A1, fill=RED + (238,), width=I(S * 0.012))

# ---- 输出 ----
out = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
out.save("/Users/apple/projects/screen-bridge/assets/icon_1024.png")
print("saved icon_1024.png (v16 标准投屏符号：屏幕+三角 / 安卓绿点 / 鸿蒙红弧)")
