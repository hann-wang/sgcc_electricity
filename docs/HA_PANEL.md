# Home Assistant 面板集成指南

将 Web 控制台直接嵌入到 Home Assistant 左侧菜单中，点击即可全屏访问。

## 配置方法（推荐：Webpage 仪表盘）

Home Assistant 2024.4+ 已移除 `panel_iframe` YAML 配置，改用 **Webpage 仪表盘**。通过 UI 操作即可完成，无需编辑 YAML。

### 配置步骤

#### 1. 打开仪表盘管理页面

在 Home Assistant 中：

1. 进入 **设置** → **仪表盘**
2. 点击右下角 **添加仪表盘**

#### 2. 创建 Webpage 仪表盘

1. 选择 **Webpage（网页）**
2. 填写配置：

| 字段 | 值 |
|------|-----|
| 名称 | `国家电网电费数据` |
| 图标 | `mdi:lightning-bolt` |
| URL | `http://homeassistant.local:8080` |

> URL 中的 `homeassistant.local` 替换为你的 HA 实际地址。Add-on 方式下可直接用 `http://homeassistant:8123` 对应主机的地址加 `:8080`。

3. 点击 **创建**

#### 3. 完成

创建后，左侧菜单底部会出现「国家电网电费数据」入口，点击即可全屏访问 Web 控制台。

```
┌─────────────────────────────┐
│ Home Assistant              │
├─────────────────────────────┤
│ 🏠 Overview                  │
│ 📊 Dashboard                 │
│ ⚙️ Settings                  │
├─────────────────────────────┤
│ ⚡ 国家电网电费数据           │  ← 新增入口
└─────────────────────────────┘
```

## 方法二：使用 iframe 卡片嵌入到现有仪表盘

如果你想在现有仪表盘页面中嵌入 Web 控制台，可以使用 iframe 卡片：

1. 进入要编辑的仪表盘页面
2. 点击右上角三点菜单 → **编辑仪表盘**
3. 点击 **添加卡片**
4. 选择 **iframe** 卡片
5. 填写：

| 字段 | 值 |
|------|-----|
| URL | `http://homeassistant.local:8080` |
| 宽高比 | `75%`（可选） |

6. 保存

## URL 地址说明

根据部署方式选择正确的 URL：

| 部署方式 | URL |
|---------|-----|
| Docker Compose（同网络） | `http://ha_sgcc_electricity:8080`（容器名） |
| Docker Compose（同主机） | `http://host.docker.internal:8080` |
| Add-on | `http://homeassistant.local:8080`（或 HA 的 IP:8080） |
| 远程服务器 | `http://服务器IP:8080` |

> **提示**：在浏览器中先直接访问该 URL，确认能打开 Web 控制台后再配置。

## 安全性

### 设置 Web 控制台密码

在 `.env` 或 Add-on 配置中设置密码：

```env
WEB_DASHBOARD_PASSWORD=your_secure_password
```

### 限制仪表盘可见性

创建 Webpage 仪表盘时可以设置为仅管理员可见，避免其他用户看到。

## 故障排查

### 问题 1：无法访问 Web 控制台

**症状**：点击菜单项后显示空白或无法连接

**解决方案**：
1. 确认 Web 控制台服务是否运行：直接在浏览器访问 `http://HA地址:8080`
2. 检查 Docker 端口映射是否正确：`8080:8080`
3. 确认 URL 地址是否正确
4. 检查防火墙设置

### 问题 2：显示空白页面

**症状**：页面加载但显示空白

**解决方案**：
1. 按浏览器 F12 打开开发者工具，查看 Console 是否有错误
2. 确认 Web 控制台是否正常启动（查看 Add-on 日志）
3. 检查是否有跨域（CORS）问题

### 问题 3：panel_iframe 报错

**症状**：`Integration 'panel_iframe' not found`

**解决方案**：

这是 Home Assistant 2024.4+ 的正常行为。`panel_iframe` 已被移除，请使用上方介绍的 **Webpage 仪表盘** 方法：

1. 从 `configuration.yaml` 中删除所有 `panel_iframe:` 相关配置
2. 重启 Home Assistant
3. 按上方「配置步骤」通过 UI 创建 Webpage 仪表盘

> 如果之前有 `panel_iframe` YAML 配置，HA 会在升级时自动迁移到 Webpage 仪表盘。你只需删除 YAML 中的旧配置并重启即可。

## 移动端

Web 控制台支持移动端访问：

1. 使用 Home Assistant Companion App 访问效果最佳
2. 仪表盘入口会自动出现在 App 侧边栏
3. 横屏查看图表效果更好
