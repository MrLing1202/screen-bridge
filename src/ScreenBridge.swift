import Cocoa

final class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var scrcpyProcess: Process?
    var currentSerial: String?

    private var macosDir: String { Bundle.main.bundlePath + "/Contents/MacOS" }
    private var adbPath: String { macosDir + "/adb" }
    private var scrcpyPath: String { macosDir + "/scrcpy" }

    func applicationDidFinishLaunching(_ notification: Notification) {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        rebuildMenu()
        refreshState()
        Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            self.refreshState()
        }
    }

    // MARK: - 设备发现

    func adbDevices() -> [(serial: String, kind: String)] {
        let out = runShell("\(adbPath) devices -l 2>/dev/null")
        var result: [(String, String)] = []
        for line in out.components(separatedBy: "\n") {
            let parts = line.split(separator: " ").map(String.init)
            guard parts.count >= 2, parts[1] == "device" else { continue }
            let serial = parts[0]
            let kind = line.contains("usb:") ? "USB" : "无线"
            result.append((serial, kind))
        }
        return result
    }

    func findTargetSerial() -> (serial: String, kind: String)? {
        let devices = adbDevices()
        // USB 优先，无线兜底
        if let usb = devices.first(where: { $0.kind == "USB" }) { return usb }
        return devices.first
    }

    // MARK: - 状态

    func isRunning() -> Bool {
        scrcpyProcess != nil && scrcpyProcess!.isRunning
    }

    func refreshState() {
        DispatchQueue.main.async {
            let running = self.isRunning()
            self.statusItem.button?.image = self.menuImage(active: running)
            self.statusItem.button?.toolTip = running ? "手机投屏运行中" : "手机投屏已停止"
            if let menu = self.statusItem.menu, menu.items.count > 0 {
                menu.items[0].title = running ? "停止投屏" : "启动投屏"
            }
        }
    }

    func rebuildMenu() {
        let menu = NSMenu()
        let toggleItem = NSMenuItem(title: "启动投屏", action: #selector(toggle), keyEquivalent: "")
        toggleItem.target = self
        menu.addItem(toggleItem)
        menu.addItem(NSMenuItem.separator())

        let devices = adbDevices()
        if devices.isEmpty {
            let item = NSMenuItem(title: "未检测到手机（请用 USB 连接并开启调试）", action: nil, keyEquivalent: "")
            item.isEnabled = false
            menu.addItem(item)
        } else {
            for d in devices {
                let item = NSMenuItem(title: "\(d.kind) · \(d.serial)", action: nil, keyEquivalent: "")
                item.isEnabled = false
                menu.addItem(item)
            }
        }

        menu.addItem(NSMenuItem.separator())
        let quitItem = NSMenuItem(title: "退出", action: #selector(quit), keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)
        statusItem.menu = menu
    }

    // MARK: - 启停

    @objc func toggle() {
        if isRunning() {
            stop()
        } else {
            start()
        }
    }

    func start() {
        guard let target = findTargetSerial() else {
            showAlert("未检测到手机", "请用 USB 数据线连接手机，并在手机设置中开启「开发者选项 → USB 调试」。连接后再次点击启动。")
            return
        }
        currentSerial = target.serial

        let p = Process()
        p.executableURL = URL(fileURLWithPath: scrcpyPath)
        p.arguments = ["-s", target.serial, "--max-size", "1600", "--video-codec", "h264"]
        p.terminationHandler = { _ in
            DispatchQueue.main.async { self.refreshState() }
        }
        do {
            try p.run()
            scrcpyProcess = p
        } catch {
            showAlert("启动失败", "无法启动 scrcpy：\(error.localizedDescription)")
        }
        refreshState()
        // 设备列表可能变化，刷新菜单
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { self.rebuildMenu() }
    }

    func stop() {
        scrcpyProcess?.terminate()
        scrcpyProcess = nil
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { self.refreshState() }
    }

    // MARK: - UI

    /// 菜单栏图标：直接使用内置 AppIcon（深蓝紫底+屏幕+绿点）。
    /// 运行态保持原色（绿点醒目），停止态转灰度+半透明，一眼区分状态。
    func menuImage(active: Bool) -> NSImage {
        let base: NSImage
        if let iconPath = Bundle.main.pathForImageResource("AppIcon"),
           let icon = NSImage(contentsOfFile: iconPath) {
            base = icon
        } else {
            base = NSImage(size: NSSize(width: 22, height: 22))
        }
        let target = NSSize(width: 18, height: 18)
        let resized = NSImage(size: target)
        resized.lockFocus()
        NSGraphicsContext.current?.imageInterpolation = .high
        base.draw(in: NSRect(origin: .zero, size: target),
                  from: NSRect(origin: .zero, size: base.size),
                  operation: .copy, fraction: active ? 1.0 : 0.55)
        resized.unlockFocus()

        if active { return resized }

        // 停止态：灰度化
        guard let cg = resized.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            return resized
        }
        let ci = CIImage(cgImage: cg)
        guard let filter = CIFilter(name: "CIPhotoEffectMono") else { return resized }
        filter.setValue(ci, forKey: kCIInputImageKey)
        guard let output = filter.outputImage else { return resized }
        let rep = NSCIImageRep(ciImage: output)
        let gray = NSImage(size: rep.size)
        gray.addRepresentation(rep)
        return gray
    }

    func showAlert(_ title: String, _ message: String) {
        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = message
        alert.alertStyle = .warning
        alert.runModal()
    }

    // MARK: - 工具

    func runShell(_ command: String) -> String {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/bin/bash")
        p.arguments = ["-c", command]
        let pipe = Pipe()
        p.standardOutput = pipe
        p.standardError = pipe
        do { try p.run() } catch { return "" }
        p.waitUntilExit()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return String(data: data, encoding: .utf8) ?? ""
    }

    @objc func quit() {
        stop()
        NSApp.terminate(nil)
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory)
app.run()
