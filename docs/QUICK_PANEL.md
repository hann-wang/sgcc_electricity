# 快速集成到 Home Assistant 界面

> Home Assistant 2024.4+ 已移除 `panel_iframe`，不再支持 YAML 配置。请按以下步骤通过 UI 操作。

## 3 步完成

### 1. 打开仪表盘管理

点击 **设置** → **仪表盘** → 右下角 **添加仪表盘**

### 2. 创建 Webpage 仪表盘

选择 **Webpage（网页）**，填写：

- **名称**：`国家电网电费数据`
- **图标**：`mdi:lightning-bolt`
- **URL**：`http://homeassistant.local:8080`

> `homeassistant.local` 替换为你的 HA 实际地址。

### 3. 完成

左侧菜单底部出现「国家电网电费数据」入口，点击即可全屏访问。

## 如果你之前配置了 panel_iframe（报错修复）

出现 `Integration 'panel_iframe' not found` 是因为新版本已移除该集成。

**修复步骤**：

1. 编辑 `configuration.yaml`，删除所有 `panel_iframe:` 相关内容
2. 重启 Home Assistant（旧配置会自动迁移）
3. 如未自动迁移，按上面 3 步手动创建

详细说明见 [HA_PANEL.md](HA_PANEL.md)。
