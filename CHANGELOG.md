# 更新日志

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.1.0] - 2026-06-11

### 新增

- **Web 控制台**：浏览器查看多户用电概览、阶梯用电、日/月图表、运行日志，手动触发同步（`WEB_DASHBOARD=true`）
- **ENABLE_HA_PUSH 参数**：支持通过环境变量控制是否推送数据到 Home Assistant（默认 `true`），设为 `false` 时仅抓取数据存入数据库
- **项目定位调整**：从 HA 集成工具重新定位为国家电网数据获取工具，HA 推送为可选功能

### 修复

- **MQTT 实体命名**：修复 MQTT Discovery 实体 ID 生成拼音化问题，正确使用 `object_id` + `default_entity_id`（兼容 HA 2025.10+）
- **MQTT 连接稳定性**：修复多实例共用 client_id 导致的意外断连，每个连接自动追加唯一后缀
- **容器重启后按钮状态**：容器异常重启后自动检测并重置任务锁状态，"立即运行"按钮不再被卡住
- **日志清空后无法输出**：修复清空日志文件后写入失效的问题
- **日志轮转**：切换为按天轮转，保留 30 天

### 变更

- **Docker 镜像名**：`ha_sgcc_electricity` → `sgcc_electricity`
- **GitHub 仓库迁移**：`Poiig/ha_sgcc_electricity` → `Poiig/sgcc_electricity`
- **基础镜像托管**：统一推送到 Docker Hub（`poiigzhao/sgcc_electricity:base`）

### 升级指引

1. 更新镜像名：将 `ha_sgcc_electricity` 替换为 `sgcc_electricity`
2. 更新仓库地址：`https://github.com/Poiig/sgcc_electricity`
3. Docker 用户拉取新镜像后 `docker compose up -d --force-recreate`
4. Add-on 用户更新仓库 URL 后重新安装

---

## [2.0.0] - 2026-06-02

### 新增

- **Home Assistant Add-on**：支持从 HA 加载项商店安装（`Poiig/sgcc_electricity`）
- **企业微信汇总推送**：抓取成功后推送多户 Markdown 汇总（余额、日/月/年用电、当月分时、应交金额）
- **当月分时传感器**：从 `daily_usage` 表 SQL 汇总当前自然月谷/平/峰/尖电量
- **阶梯用电传感器**：住宅用户一/二/三阶已用、剩余、当前阶段等
- **豆包大模型验证码**：`CAPTCHA_SOLVER=llm`，支持点选 + 滑块（详见 [docs/LLM_CAPTCHA.md](docs/LLM_CAPTCHA.md)）
- **本地 OCR 验证码**：`CAPTCHA_SOLVER=local`（ddddocr + 图像匹配，默认）
- **二维码登录与 fallback**：`LOGIN_METHOD=qrcode` / `LOGIN_FALLBACK=qrcode`，失败原因推送至企微
- **Docker 部署**：headless Chromium、`RUN_ON_STARTUP` 启动即抓取
- **数据库**：默认 SQLite；可选 MySQL；统一 6 表结构，可配置保留天数
- **国内镜像加速**：GHCR / Docker Hub 加速地址（见 README）

### 修复

- **多户余额拉取错误**：修复切换户号后整页刷新导致多户余额相同的问题
- **CDP 兼容**：默认跳过 CDP stealth 注入，避免 Selenium 4.34 + Chromium 148 下 `Runtime.evaluate` 错误
- **Docker headless viewport**：无头模式下显式设置窗口尺寸与 CDP viewport
- **Windows 中文日志**：UTF-8 终端输出与 `.env` override 加载
- **RK001 风控**：登录失败指数退避重试

### 变更

- 环境变量统一为 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`（豆包默认已写入 `example.env`）
- Add-on 配置项 `llm_api_key` 替代旧 `ark_api_key`
- README 精简，大模型接入详情移至 `docs/LLM_CAPTCHA.md`
- CI：Docker 镜像改为手动 workflow 发布

### 升级指引

1. 备份 `.env` 或 Add-on 配置
2. 若曾使用 `ARK_*`，改为对应 `LLM_*` 变量
3. 数据库默认启用 SQLite（勿将 `DB_TYPE` 留空）
4. Docker 用户拉取新镜像后 `docker compose up -d --force-recreate`
5. Add-on 用户保存配置并重启加载项

---

## [1.7.3] 及更早

见 [GitHub Releases](https://github.com/Poiig/sgcc_electricity/releases) 历史版本（上游 ARC-MX 镜像 tag：`v1.4.0` ~ `v1.7.3`）。

[2.1.0]: https://github.com/Poiig/sgcc_electricity/releases/tag/v2.1.0
[2.0.0]: https://github.com/Poiig/sgcc_electricity/releases/tag/v2.0.0
