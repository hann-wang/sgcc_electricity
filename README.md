# 国家电网电费数据获取

[![Docker Build](https://github.com/Poiig/ha_sgcc_electricity/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Poiig/ha_sgcc_electricity/actions/workflows/docker-publish.yml)

将国家电网（95598）的电费、用电量、分时电量、阶梯用电数据接入 Home Assistant，支持验证码自动识别。

## 致谢

- [ARC-MX/sgcc_electricity_new](https://github.com/ARC-MX/sgcc_electricity_new) — 项目基础框架和数据抓取逻辑
- [renxiaoyaoo/ha-95598](https://github.com/renxiaoyaoo/ha-95598) — 点选验证码识别方案参考

本项目遵循 Apache License 2.0 协议。[更新日志](docs/CHANGELOG.md)

---

## 功能亮点

- 自动登录国家电网（支持点选/滑块验证码自动识别、二维码扫码登录）
- **两种数据推送方式**：REST API 和 MQTT Discovery（自动创建实体，无需手动配置）
- 支持每日/月度/年度分时电量（谷/平/峰/尖）采集
- 支持住宅用户阶梯用电数据（一/二/三阶已用、剩余、当前阶段）
- **Web 控制台**：浏览器查看运行日志、户号图表、手动触发同步
- 数据库支持 SQLite / MySQL / PostgreSQL
- 电费余额不足通知（PushPlus / URL / 企业微信）
- 适用于国家电网覆盖省份（`linux/amd64`、`linux/arm64`）

---

## 数据推送方式

本项目支持两种方式将数据推送到 Home Assistant：

| 对比维度 | REST API | MQTT Discovery |
|---------|---------|---------------|
| **配置复杂度** | 需配置 template | 只需配置 MQTT 地址 |
| **实体创建** | 手动配置 template | 自动发现创建 |
| **配置说明** | [REST API 配置指南](docs/HA_CONFIG.md) | [MQTT 使用指南](docs/MQTT.md) |
| **兼容性** | 所有 HA 版本 | 需要 MQTT 集成 |
| **状态保持** | 需要缓存恢复 | retain 消息自动保持 |
| **网络开销** | HTTP 协议 | 轻量级 MQTT |

> **推荐**：MQTT Discovery 方式配置更简单，实体自动创建，详见 [MQTT 使用指南](docs/MQTT.md)。
>
> REST API 方式需要在 HA 的 `configuration.yaml` 中配置 template，详见 [REST API 配置指南](docs/HA_CONFIG.md)。

两种方式共享相同的实体命名（`sensor.xxx_xxxx`），现有卡片无需修改即可在两种方式间切换。

---

## Web 控制台

启用 `WEB_DASHBOARD=true` 后，访问 `http://<主机>:8080/` 查看多户用电概览、阶梯用电、日/月图表与同步记录。

**集成到 Home Assistant 界面**：通过 HA 的 **Webpage 仪表盘** 功能，可将 Web 控制台直接嵌入左侧菜单。详见 [面板集成指南](docs/HA_PANEL.md) 或 [快速指南](docs/QUICK_PANEL.md)。

![Web 控制台登录页](docs/attachment/login.png)

![Web 控制台监控页](docs/attachment/controller.png)

---

## 安装部署

### 方式一：Home Assistant Add-on（推荐）

1. 进入 `设置` → `加载项` → `加载项商店`
2. 右上角 `...` → `仓库`，添加：`https://github.com/Poiig/ha_sgcc_electricity`
3. 刷新页面，找到 **国家电网电费数据获取** 并安装
4. 切换到 `配置` 标签，填写手机号、密码
5. 配置推送方式：填写 `hass_url` + `hass_token`（REST API）或 `mqtt_host`（MQTT）
6. 保存配置，启动 Add-on

### 方式二：Docker Compose

```bash
mkdir ha_sgcc_electricity && cd ha_sgcc_electricity
curl -O https://raw.githubusercontent.com/Poiig/ha_sgcc_electricity/master/docker-compose.yml
curl -O https://raw.githubusercontent.com/Poiig/ha_sgcc_electricity/master/example.env
cp example.env .env && vim .env
docker compose up -d --force-recreate
```

**镜像地址：**

| 来源 | 地址 |
|------|------|
| GHCR | `ghcr.io/poiig/ha_sgcc_electricity:latest` |
| GHCR 国内加速 | `ghcr.nju.edu.cn/poiig/ha_sgcc_electricity:latest` |
| Docker Hub | `poiigzhao/ha_sgcc_electricity:latest` |
| Docker Hub 国内加速 | `docker.1ms.run/poiigzhao/ha_sgcc_electricity:latest` |

### 方式三：本地运行

详见 [本地开发指南](LOCAL_DEV_GUIDE.md)

---

## 环境变量

Docker Compose 方式通过 `.env` 文件配置，完整配置项见 `example.env`。

**必填：**

| 变量 | 说明 |
|------|------|
| `PHONE_NUMBER` | 95598 登录手机号 |
| `PASSWORD` | 95598 登录密码 |
| `HASS_URL` + `HASS_TOKEN` | REST API 方式（二选一） |
| `MQTT_HOST` | MQTT 方式（二选一） |

**常用可选：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `JOB_START_TIME` | `09:30` | 每天同步开始时间（程序会在该时间及 +12 小时各执行一次） |
| `RUN_ON_STARTUP` | `false` | Docker 启动后立即登录抓取 |
| `CAPTCHA_SOLVER` | `local` | 验证码识别（推荐 `llm`，详见下方说明） |
| `DB_TYPE` | sqlite | 数据库类型（sqlite / mysql / postgresql / none） |
| `LOGIN_METHOD` | password | 登录方式（password / qrcode） |
| `LOGIN_FALLBACK` | qrcode | 登录失败备选（qrcode / none） |
| `IGNORE_USER_ID` | 空 | 忽略的户号（逗号分隔） |
| `WEB_DASHBOARD` | true | 启用 Web 控制台 |
| `PUSH_TYPE` | none | 通知方式（none / pushplus / urlpush / wework） |
| `DATA_RETENTION_DAYS` | 365 | 数据库记录保留天数，0 表示永久保留 |

---

## 传感器列表

| 实体 | 说明 |
|------|------|
| `sensor.electricity_charge_balance_xxxx` | 电费余额（元） |
| `sensor.last_electricity_usage_xxxx` | 最近一天用电量（kWh） |
| `sensor.yearly_electricity_usage_xxxx` | 今年总用电量（kWh） |
| `sensor.yearly_electricity_charge_xxxx` | 今年总电费（元） |
| `sensor.month_electricity_usage_xxxx` | 上月用电量（kWh） |
| `sensor.month_electricity_charge_xxxx` | 上月电费（元） |
| `sensor.month_valley_usage_xxxx` | 当月谷时用电量（kWh，**需启用数据库**） |
| `sensor.month_flat_usage_xxxx` | 当月平时用电量（kWh，**需启用数据库**） |
| `sensor.month_peak_usage_xxxx` | 当月峰时用电量（kWh，**需启用数据库**） |
| `sensor.month_tip_usage_xxxx` | 当月尖时用电量（kWh，**需启用数据库**） |
| `sensor.prepay_balance_xxxx` | 应交金额（元） |
| `sensor.step_used_step1_xxxx` | 阶梯一阶已用电量（kWh，住宅用户） |
| `sensor.step_remain_step1_xxxx` | 阶梯一阶剩余电量（kWh，住宅用户） |
| `sensor.step_used_step2_xxxx` | 阶梯二阶已用电量（kWh，住宅用户） |
| `sensor.step_remain_step2_xxxx` | 阶梯二阶剩余电量（kWh，住宅用户） |
| `sensor.step_used_step3_xxxx` | 阶梯三阶已用电量（kWh，住宅用户） |
| `sensor.step_total_usage_xxxx` | 阶梯累计用电量（kWh，住宅用户） |
| `sensor.step_stage_xxxx` | 当前阶梯阶段（1/2/3，住宅用户） |

> `xxxx` 为户号后四位。

---

## 数据库

| `DB_TYPE` | 说明 |
|-----------|------|
| `sqlite` | **默认**。本地文件，适合单机 / Docker 部署 |
| `mysql` | 连接外部 MySQL |
| `postgresql` | 连接外部 PostgreSQL |
| `none` | 不写入数据库；当月分时传感器不会更新 |

启用数据库后程序自动建表，详见 [数据库表结构说明](docs/DATABASE.md)。

当月谷/平/峰/尖传感器依赖数据库从 `daily_usage` 表 SQL 汇总，`DB_TYPE=none` 时这四个传感器不会更新。

---

## 验证码识别

| 模式 | 配置值 | 说明 |
|------|--------|------|
| 大模型视觉识别（**推荐**） | `llm` | 火山引擎豆包大模型，识别率高，支持点选 + 滑块 |
| 本地 OCR | `local` | 免费，基于 ddddocr + 图像匹配，适合点选验证码，存在识别失败的情况 |

> **推荐使用 `llm` 模式**：本地 OCR 方案基于图像匹配，受验证码样式变化影响较大，存在识别失败的情况。大模型方式识别率更高且同时支持点选和滑块验证码。
>
> 两种方式的详细配置说明见 [验证码接入指南](docs/LLM_CAPTCHA.md)。如不想处理验证码，可直接使用 `LOGIN_METHOD=qrcode` 扫码登录。

---

## 常见问题

详见 [常见问题文档](docs/FAQ.md)，涵盖验证码识别、传感器数据、数据库选择、HA 集成等常见问题。

---

## License

[Apache License 2.0](LICENSE)
