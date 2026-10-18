
# Third-Party Notices

ScreenBridge 依赖以下第三方组件。本仓库不包含第三方二进制文件；
构建产物中的 scrcpy / adb / scrcpy-server 二进制来自各项目官方 Release 包。

## scrcpy — GPL-3.0

- 项目：https://github.com/Genymobile/scrcpy
- 用途：屏幕镜像核心引擎（`scrcpy` 可执行文件与 `scrcpy-server`）
- 许可证：GNU General Public License v3.0（GPL-3.0）
- 来源：官方 Release 包 `scrcpy-macos-aarch64-v5.0.1`
- 合规说明：
  - ScreenBridge 通过独立进程命令行方式调用 scrcpy，不链接、不修改其源码；
  - 构建产物中包含 scrcpy 二进制，分发构建产物时请自行遵守 GPL-3.0 相关条款
    （例如向最终用户提供获取对应源码的途径与完整许可证文本）；
  - scrcpy 完整许可证文本见官方包内 `LICENSE` 文件。

## adb（Android Debug Bridge）— Apache-2.0

- 项目：https://android.googlesource.com/platform/tools/adb （Android Platform Tools）
- 用途：Android 设备发现、连接与调试
- 许可证：Apache License 2.0
- 来源：scrcpy 官方 macOS 包内置的 `adb` 可执行文件
- 合规说明：Apache-2.0 允许以二进制形式分发，需保留原始版权声明与许可证文本。

## 图标设计

- 图标为 ScreenBridge 原创设计（鸿蒙蓝紫渐变背景 + Android 绿色机器人 + 鸿蒙 H 符号），
  使用 Python 脚本 `assets/make_icon.py` 程序化生成，归属于本项目 MIT License。

---

> 本声明仅作善意合规提示，不构成法律意见。请在分发前咨询专业人士确认许可合规性。
