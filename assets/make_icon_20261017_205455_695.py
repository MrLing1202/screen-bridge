#!/usr/bin/env python3
"""ScreenBridge 图标 v15 —— 成熟投屏 Logo
设计语言（产品级，告别吉祥物）：
- 深蓝紫对角渐变底 + 中央柔光（商业感、克制）
- 白色圆角屏幕符号（主体，单焦点）
- 屏内安卓绿圆点（#3DDC84，代表被投屏的安卓设备）
- 屏顶鸿蒙红信号弧（#E60012，无线投屏语义 + 鸿蒙元素）
构图：一个符号、两个品牌色点缀、大量留白。
"""
from PIL import Image, ImageDraw, ImageFilter

S = 4096
OUT = 1024
cx, cy = S // 2, S // 2

def I(x):
    return int(round(x))

# ---- 深蓝紫对角渐变背景（4x4 双三次放大，快且平滑）----
small = Image.new("RGB", (4, 4))
TL = (0x26, 0x36, 0x5E); TR = (0x1B, 0x29, 0x4B)
BL = (0x33, 0x2B, 0x6E); BR = (0x16, 0x1B, 0x3A)
small.putpixel((0, 0), TL); small.putpixel((3, 0), TR)
small.putpixel((0, 3), BL); small.putpixel((3, 3), BR)
img = small.resize((S, S), Image.BICUBIC).convert("RGBA")

# 中央柔光
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([cx - I(S * 0.34), cy - I(S * 0.34),
            cx + I(S * 0.34), cy + I(S * 0.34)],
           fill=(130, 165, 255, 42))
glow = glow.filter(ImageFilter.GaussianBlur(I(S * 0.13)))
img = Image.alpha_composite(img, glow)
dr = ImageDraw.Draw(img, "RGBA")

# ---- 白色屏幕符号（带底部投影）----
sw, sh = I(S * 0.315), I(S * 0.360)          # 屏幕宽高
scx = cx
scy = I(cy + S * 0.030)                      # 屏幕中心略偏下，给顶部弧留空间
sx0, sy0 = scx - sw // 2, scy - sh // 2
radius = I(S * 0.095)

# 投影
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([sx0, sy0 + I(S * 0.020),
                      sx0 + sw, sy0 + sh + I(S * 0.020)],
                     radius=radius, fill=(0, 0, 0, 90))
shadow = shadow.filter(ImageFilter.GaussianBlur(I(S * 0.045)))
img = Image.alpha_composite(img, shadow)
dr = ImageDraw.Draw(img, "RGBA")

# 屏幕本体（纯白，干净）
dr.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh],
                     radius=radius, fill=(255, 255, 255, 255))

# ---- 安卓绿圆点（屏内，代表安卓设备）----
d_r = I(S * 0.030)
dcx, dcy = scx, I(scy + S * 0.050)
dglow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
dd = ImageDraw.Draw(dglow)
dd.ellipse([dcx - I(d_r * 2.6), dcy - I(d_r * 2.6),
            dcx + I(d_r * 2.6), dcy + I(d_r * 2.6)],
           fill=(0x3D, 0xDC, 0x84, 60))
dglow = dglow.filter(ImageFilter.GaussianBlur(I(S * 0.030)))
img = Image.alpha_composite(img, dglow)
dr = ImageDraw.Draw(img, "RGBA")
dr.ellipse([dcx - d_r, dcy - d_r, dcx + d_r, dcy + d_r],
           fill=(0x3D, 0xDC, 0x84, 255))

# ---- 鸿蒙红信号弧（两条，从屏幕后部向上发出）----
RED = (0xE6, 0x00, 0x12)
arc_cx, arc_cy = scx, I(scy - S * 0.130)     # 圆心藏在屏幕顶边之后
A0, A1 = 198, 342

# 外弧发光
halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
for rr, ww in ((I(S * 0.150), I(S * 0.030)), (I(S * 0.088), I(S * 0.030))):
    hd.arc([arc_cx - rr, arc_cy - rr, arc_cx + rr, arc_cy + rr],
           A0, A1, fill=RED + (50,), width=ww)
halo = halo.filter(ImageFilter.GaussianBlur(I(S * 0.018)))
img = Image.alpha_composite(img, halo)
dr = ImageDraw.Draw(img, "RGBA")

# 实线弧
for rr in (I(S * 0.150), I(S * 0.088)):
    dr.arc([arc_cx - rr, arc_cy - rr, arc_cx + rr, arc_cy + rr],
           A0, A1, fill=RED + (235,), width=I(S * 0.012))

# ---- 输出 ----
out = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
out.save("/Users/apple/projects/screen-bridge/assets/icon_1024.png")
print("saved icon_1024.png (v15 成熟投屏Logo：白屏幕 + 安卓绿点 + 鸿蒙红弧)")
