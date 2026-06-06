# Home Assistant 面板集成指南

本指南介绍如何将 Web 控制台直接嵌入到 Home Assistant 界面中。

## 方法一：使用 Panel Iframe 集成（推荐）

### 优点
- ✅ 配置简单，几行即可
- ✅ 在左侧菜单添加独立入口
- ✅ 全屏显示，体验最佳
- ✅ HA 内置集成，无需安装
- ✅ 移动端支持良好

### 配置步骤

#### 1. 配置 Web 控制台端口映射

确保 Web 控制台端口可以从 Home Assistant 访问：

**Docker Compose 方式**：

在 `docker-compose.yml` 中确保端口映射正确：

```yaml
ports:
  - "8080:8080"  # Web 控制台端口
```

**Home Assistant Add-on 方式**：

端口会自动配置为 `8080`，无需额外配置。

#### 2. 配置 Home Assistant Panel Iframe

编辑 `configuration.yaml`，添加以下配置：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

如果 Web 控制台设置了密码保护，需要在 URL 中包含认证信息：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

#### 3. 重启 Home Assistant

```bash
# 在 Home Assistant 界面中：Settings → System → YAML → 重启
# 或在终端中：
ha core restart
```

#### 4. 访问 Web 控制台

重启后，在 Home Assistant 左侧菜单底部会看到"国家电网"入口，点击即可访问。

## 方法二：使用 Markdown Card 嵌入 iframe

如果你想在现有仪表盘中嵌入 Web 控制台，可以使用 Markdown Card：

```yaml
title: 家庭仪表盘
views:
  - title: 主页
    cards:
      - type: markdown
        content: |
          ## 国家电网电费数据
          <iframe src="http://homeassistant.local:8080" width="100%" height="600" frameborder="0"></iframe>
```

## 方法三：使用自定义面板（高级）

如果需要更深度的集成，可以创建自定义面板：

### 1. 创建面板目录

```bash
mkdir -p /config/custom_components/sgcc_panel
```

### 2. 创建 manifest.json

```json
{
  "domain": "sgcc_panel",
  "name": "国家电网面板",
  "version": "1.0.0",
  "documentation": "https://github.com/Poiig/ha_sgcc_electricity",
  "dependencies": [],
  "codeowners": [],
  "iot_class": "local_polling"
}
```

### 3. 创建 __init__.py

```python
from homeassistant.components.panel_custom import register_panel

DOMAIN = "sgcc_panel"

async def async_setup(hass, config):
    register_panel(
        hass,
        component_name="sgcc_panel",
        frontend_url_path="sgcc",
        sidebar_title="国家电网",
        sidebar_icon="mdi:lightning-bolt",
        require_admin=True,
        config={
            "embed_iframe": True,
            "url": "http://homeassistant.local:8080"
        }
    )
    return True
```

### 4. 重启 Home Assistant

## 网络配置

### Docker Compose 网络

如果 Web 控制台和 Home Assistant 在同一个 Docker 网络中，可以使用服务名称：

```yaml
services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    networks:
      - ha_network

  ha_sgcc_electricity:
    image: poiigzhao/ha_sgcc_electricity:latest
    networks:
      - ha_network
    ports:
      - "8080:8080"

networks:
  ha_network:
    driver: bridge
```

然后在 `configuration.yaml` 中使用服务名称：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://ha_sgcc_electricity:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

### Add-on 网络

Home Assistant Add-on 默认与 Home Assistant 在同一个网络中，可以直接使用：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://192.168.1.100:8123/api/hassio_ingress/XXXXX"
    icon: mdi:lightning-bolt
    require_admin: true
```

其中 `XXXXX` 需要替换为实际的 ingress 路径。

## 安全性考虑

### 1. 设置 Web 控制台密码

在 `.env` 或 Add-on 配置中设置密码：

```env
WEB_DASHBOARD_PASSWORD=your_secure_password
```

### 2. 使用 HTTPS

如果 Web 控制台暴露在公网，建议配置 HTTPS：

#### 使用 Nginx 反向代理

```nginx
location /sgcc/ {
    proxy_pass http://localhost:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

然后在 `configuration.yaml` 中：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "https://your-domain.com/sgcc/"
    icon: mdi:lightning-bolt
    require_admin: true
```

### 3. 限制访问

设置 `require_admin: true` 确保只有管理员可以访问。

## 移动端适配

Web 控制台已经支持移动端，但在手机上访问时，建议：

1. 横屏使用获得更好的图表显示效果
2. 使用 Home Assistant Companion App 访问
3. 在移动端添加到主屏幕，像原生应用一样使用

## 故障排查

### 问题 1：无法访问 Web 控制台

**症状**：点击菜单项后显示"无法连接"

**解决方案**：
1. 确认 Web 控制台服务是否运行
2. 检查端口映射是否正确
3. 确认 URL 地址是否正确
4. 检查防火墙设置

### 问题 2：显示空白页面

**症状**：iframe 加载但显示空白

**解决方案**：
1. 检查浏览器控制台是否有错误
2. 确认 Web 控制台是否正常启动
3. 检查是否有 CORS 问题

### 问题 3：需要频繁登录

**症状**：每次访问都需要输入密码

**解决方案**：
1. 检查 Session TTL 设置
2. 确认浏览器是否允许 Cookie
3. 检查 Web 控制台日志中的 session 信息

## 推荐配置

以下是推荐的完整配置：

### Docker Compose + Panel Iframe

```yaml
# docker-compose.yml
services:
  ha_sgcc_electricity:
    image: poiigzhao/ha_sgcc_electricity:latest
    restart: unless-stopped
    environment:
      - PHONE_NUMBER=your_phone_number
      - PASSWORD=your_password
      - WEB_DASHBOARD=true
      - WEB_DASHBOARD_PORT=8080
      - WEB_DASHBOARD_PASSWORD=your_secure_password
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
```

```yaml
# configuration.yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

### Add-on + Panel Iframe

Add-on 配置：

```yaml
web_dashboard: true
web_dashboard_password: your_secure_password
```

`configuration.yaml`：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

## 使用场景

### 场景 1：管理员监控

管理员可以在 Home Assistant 中直接监控电费数据，无需单独打开浏览器访问。

### 场景 2：家庭成员查看

家庭成员可以通过 Home Assistant 查看电费信息，了解用电情况。

### 场景 3：自动化触发

可以通过 Home Assistant 自动化，在余额低于阈值时提醒用户查看 Web 控制台。

### 场景 4：历史数据查看

可以在 Web 控制台中查看历史用电图表，了解用电趋势。

## 效果预览

配置完成后，Home Assistant 左侧菜单底部会出现"国家电网"入口：

```
┌─────────────────────────────┐
│ Home Assistant              │
├─────────────────────────────┤
│ 🏠 Overview                  │
│ 📊 Dashboard                 │
│ 📱 Mobile App                │
│ ⚙️ Settings                  │
├─────────────────────────────┤
│ ⚡ 国家电网                  │  ← 新增入口
└─────────────────────────────┘
```

点击后会全屏显示 Web 控制台界面。

## 高级功能

### 1. 自动刷新

可以设置 iframe 自动刷新，获取最新数据：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true
```

然后在 Web 控制台 JavaScript 中添加自动刷新：

```javascript
setInterval(() => {
  location.reload();
}, 5 * 60 * 1000);  // 每 5 分钟刷新
```

### 2. 深度链接

可以直接链接到特定户号或图表：

```yaml
panel_iframe:
  国家电网:
    title: 国家电网电费数据
    url: "http://homeassistant.local:8080#/user/1234567890123"
    icon: mdi:lightning-bolt
    require_admin: true
```

### 3. 多个面板

可以为不同户号创建多个面板：

```yaml
panel_iframe:
  国家电网_主页:
    title: 国家电网 - 主户号
    url: "http://homeassistant.local:8080"
    icon: mdi:lightning-bolt
    require_admin: true

  国家电网_充电桩:
    title: 国家电网 - 充电桩
    url: "http://homeassistant.local:8080#/user/9876543210987"
    icon: mdi:car-electric
    require_admin: true
```