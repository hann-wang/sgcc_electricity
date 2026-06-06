# 快速集成到 Home Assistant 界面

## 最简单的方法（推荐）

### 1. 确认 Web 控制台已启用

在 Add-on 配置中确保：

```yaml
web_dashboard: true
web_dashboard_password: ""  # 留空则无需登录，或设置密码保护
```

### 2. 编辑 Home Assistant 配置

在 Home Assistant 界面中：

1. 点击左侧 `设置` → `系统` → `YAML 配置编辑`
2. 点击 `configuration.yaml`
3. 在文件末尾添加以下内容：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

> **注意**：如果 `homeassistant.local` 无法访问，请替换为你的 HA 实际地址，例如 `192.168.1.100`

### 3. 重启 Home Assistant

在配置页面底部，点击 `重启服务器` 按钮，或点击右上角的三点菜单 → 重启服务器。

### 4. 完成！

重启后，在 Home Assistant 左侧菜单底部会看到「国家电网」入口：

```
┌─────────────────────────────┐
│ Home Assistant              │
├─────────────────────────────┤
│ 🏠 Overview                  │
│ 📊 Dashboard                 │
│ ⚙️ Settings                  │
├─────────────────────────────┤
│ ⚡ 国家电网                  │  ← 点击这里
└─────────────────────────────┘
```

点击「国家电网」，即可全屏查看 Web 控制台，包括：
- 📊 户号数据汇总
- 📈 日用电量图表
- 📅 月用电量图表
- 📋 运行日志
- ⚙️ 环境变量配置
- 🔄 手动触发同步

## 效果预览

配置完成后，Web 控制台会以全屏方式显示在 Home Assistant 中：

- ✅ 左侧菜单中有独立入口
- ✅ 全屏显示，充分利用屏幕空间
- ✅ 支持移动端访问
- ✅ 与 HA 界面风格一致
- ✅ 可设置密码保护（通过 `web_dashboard_password`）

## 故障排查

### 问题 1：点击菜单后显示"无法连接"

**解决方案**：
1. 检查 Add-on 是否正在运行
2. 确认 Web 控制台已启用（`web_dashboard: true`）
3. 尝试直接访问 `http://homeassistant.local:8080` 确认服务正常

### 问题 2：URL 地址不对

**解决方案**：
如果你的 Home Assistant 不是在 `homeassistant.local`，需要替换 URL：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://192.168.1.100:8080"  # 替换为你的 HA IP
    icon: mdi:lightning-bolt
    require_admin: true
```

### 问题 3：需要密码但不知道

**解决方案**：
如果设置了 `web_dashboard_password`，在 Add-on 配置中查看或重置密码。

## 更多功能

查看完整文档：[docs/HA_PANEL.md](../../docs/HA_PANEL.md)

包括：
- 多种集成方式对比
- 安全性配置
- 移动端适配
- 高级功能（自动刷新、深度链接等）