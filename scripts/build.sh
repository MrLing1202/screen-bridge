#!/bin/bash
# ScreenBridge 构建脚本
# 功能：编译 Swift 源码 -> 组装 ScreenBridge.app -> ad-hoc 签名 -> 打包 dmg / zip
# 用法: bash scripts/build.sh [scrcpy官方包目录]
#   可选参数: scrcpy 官方 macOS 包目录（默认使用本机已下载的包）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/src/ScreenBridge.swift"
ASSETS="$ROOT/assets"
SCRIPTS="$ROOT/scripts"
BUILD="$ROOT/build"

APP_NAME="ScreenBridge"
DISPLAY_NAME="手机投屏"
VERSION="1.0.0"
BUNDLE_ID="com.screenbridge.app"
APP="$BUILD/$APP_NAME.app"

# scrcpy 官方 macOS 包（含 scrcpy / adb / scrcpy-server / scrcpy.png / LICENSE）
SCRCPY_DIR="${1:-/Users/apple/tools/scrcpy/scrcpy-macos-aarch64-v5.0.1}"

if [ ! -d "$SCRCPY_DIR" ] || [ ! -f "$SCRCPY_DIR/scrcpy" ]; then
  echo "错误: 未找到 scrcpy 官方包目录: $SCRCPY_DIR"
  echo "请前往 https://github.com/Genymobile/scrcpy/releases 下载 scrcpy-macos-aarch64 包并传入路径"
  exit 1
fi

echo "==> [1/6] 编译 Swift 源码"
rm -rf "$BUILD"
mkdir -p "$BUILD"
swiftc -O "$SRC" -o "$BUILD/ScreenBridge"
echo "    已编译: $BUILD/ScreenBridge"

echo "==> [2/6] 检查/生成应用图标"
if [ ! -f "$ASSETS/AppIcon.icns" ]; then
  bash "$SCRIPTS/make_icon.sh"
fi

echo "==> [3/6] 组装 $APP_NAME.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BUILD/ScreenBridge"          "$APP/Contents/MacOS/ScreenBridge"
cp "$SCRCPY_DIR/adb"              "$APP/Contents/MacOS/adb"
cp "$SCRCPY_DIR/scrcpy"           "$APP/Contents/MacOS/scrcpy"
cp "$SCRCPY_DIR/scrcpy-server"    "$APP/Contents/MacOS/scrcpy-server"
cp "$SCRCPY_DIR/scrcpy.png"       "$APP/Contents/Resources/scrcpy.png"
cp "$ASSETS/AppIcon.icns"         "$APP/Contents/Resources/AppIcon.icns"
chmod +x "$APP/Contents/MacOS/ScreenBridge" \
         "$APP/Contents/MacOS/adb" \
         "$APP/Contents/MacOS/scrcpy"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$DISPLAY_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
PLIST

echo "==> [4/6] ad-hoc 签名"
codesign --force --deep --sign - "$APP"
echo "    签名完成:"
codesign -dv "$APP" 2>&1 | sed 's/^/    /'

echo "==> [5/6] 准备安装包内容"
DIST="$BUILD/dist"
rm -rf "$DIST"
mkdir -p "$DIST"
cp -R "$APP" "$DIST/"
cp "$SCRIPTS/install.sh" "$DIST/install.sh"
cp "$SCRIPTS/install.sh" "$DIST/安装.command"   # 双击即可在终端运行的安装入口
chmod +x "$DIST/install.sh" "$DIST/安装.command"

echo "==> [6/6] 打包 zip 与 dmg"
ZIP="$BUILD/ScreenBridge-$VERSION.zip"
DMG="$BUILD/ScreenBridge-$VERSION.dmg"

# zip 使用 Python zipfile 打包，确保中文文件名以 UTF-8 存储（macOS 自带 zip 会乱码）
python3 - "$ZIP" "$DIST" <<'PY'
import sys, zipfile, os
zip_path, dist = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(dist):
        for f in files:
            fp = os.path.join(root, f)
            arc = os.path.relpath(fp, dist)
            z.write(fp, arc)
            z.getinfo(arc).flag_bits |= 0x800  # 设置 UTF-8 文件名标志
print("zip 打包完成:", zip_path)
PY

hdiutil create -volname "ScreenBridge" -srcfolder "$DIST" -ov -format UDZO "$DMG" >/dev/null

rm -rf "$DIST"
rm -f "$BUILD/ScreenBridge"   # 清理编译中间产物（.app 内已有副本）

echo ""
echo "构建完成:"
echo "  App : $APP"
echo "  ZIP : $ZIP"
echo "  DMG : $DMG"
