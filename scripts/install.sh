#!/bin/bash
# ============================================================
#  ScreenBridge 手机投屏 · 一键安装脚本
#  自动完成：系统检查 -> 关闭旧实例 -> 复制到 /Applications
#            -> 解除 Gatekeeper 隔离 -> 启动
#  用法：双击「安装.command」，或在终端运行 ./install.sh
# ============================================================
set -euo pipefail

APP_NAME="ScreenBridge"
SRC_APP="$(cd "$(dirname "$0")" && pwd)/$APP_NAME.app"
DEST_APP="/Applications/$APP_NAME.app"

echo "=============================================="
echo "   ScreenBridge 手机投屏 · 一键安装"
echo "=============================================="

# ---- [1/4] 系统检查 ----
if [ "$(uname)" != "Darwin" ]; then
  echo "❌ 仅支持 macOS 系统。"
  read -r -p "按回车键退出..." _
  exit 1
fi
echo "[1/4] ✅ 系统检查通过（macOS）"

# ---- [2/4] 安装包完整性检查 ----
if [ ! -d "$SRC_APP" ]; then
  echo "❌ 未找到 $APP_NAME.app，请确认安装包完整（缺少 App）。"
  read -r -p "按回车键退出..." _
  exit 1
fi
echo "[2/4] ✅ 安装包检查通过"

# ---- [3/4] 关闭旧实例（若正在运行）----
if pgrep -x "$APP_NAME" >/dev/null 2>&1; then
  echo "     检测到正在运行的 $APP_NAME，正在关闭..."
  pkill -x "$APP_NAME" 2>/dev/null || true
  sleep 1
fi

# ---- 复制到 /Applications（需要管理员权限）----
echo "[3/4] ⏳ 正在复制到 /Applications"
echo "     如提示输入密码，请输入你的 Mac 开机密码（输入时不显示，属正常现象）"
if [ -d "$DEST_APP" ]; then
  sudo rm -rf "$DEST_APP"
fi
sudo ditto "$SRC_APP" "$DEST_APP"

# ---- 解除 Gatekeeper 隔离属性（允许 ad-hoc 签名 App 直接运行）----
sudo xattr -dr com.apple.quarantine "$DEST_APP" 2>/dev/null || true
sudo xattr -cr "$DEST_APP" 2>/dev/null || true
sudo chmod -R u+rwX "$DEST_APP"

echo "[4/4] ✅ 安装完成，正在启动..."
open "$DEST_APP"

echo ""
echo "=============================================="
echo "   🎉 ScreenBridge 已安装并启动！"
echo "   使用方式：点击屏幕右上角菜单栏图标"
echo "   1) 用 USB 线连接手机并开启「USB 调试」"
echo "   2) 点击「启动投屏」即可开始"
echo "=============================================="
read -r -p "按回车键关闭本窗口..." _
