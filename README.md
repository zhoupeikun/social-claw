# Claw 🦞

> 基于 AI 的数字分身系统，实现社交媒体自动化运营

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目介绍

Claw 是我的数字分身系统，通过分析我 14 年的社交媒体数据（5960 条微博），提炼人格特征，生成符合我风格的内容，并在即刻平台实现自动化运营。

### 核心能力

- **人格建模**：基于 5960 条微博数据，构建工作/生活双模式人格
- **内容生成**：接入 DeepSeek API，生成符合我风格的内容
- **自动运营**：Playwright 浏览器自动化，实现登录、发帖、互动
- **隐私保护**：明确的隐私边界和脱敏规则

### 项目背景

- **用户**: [@PrettyHugo](https://weibo.com/prettyhugo) - 腾讯前产品总监，14 年微博用户
- **数据规模**: 5960 条微博 + 20 条即刻动态
- **运营平台**: 即刻（主阵地）→ 小红书（扩展）

---

## 快速开始

### 环境要求

- Python 3.9+
- Playwright
- DeepSeek API Key

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/claw.git
cd claw

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置 API Key
cp config.example.json config.json
# 编辑 config.json，填入你的 DeepSeek API Key
```

### 配置

创建 `config.json`:

```json
{
  "deepseek_api_key": "your-api-key-here",
  "jike_username": "your-jike-username"
}
```

### 运行

#### 1. 数据采集（可选）

```bash
# 分析微博数据
python analyze_weibo.py

# 分析即刻数据
python analyze_jike_full.py
```

#### 2. 生成内容

```bash
python content_generator.py
```

#### 3. 发布到即刻

```bash
# 交互模式
python jike_v4.py

# 或使用专用发帖脚本
python post_now_2026-04-19_v1.py
```

**操作流程**:
1. 脚本打开 Chromium 浏览器
2. 扫码登录即刻
3. 登录成功后自动发帖
4. 截图保存到项目目录

---

## 项目结构

```
claw/
├── README.md                          # 项目文档
├── LICENSE                            # 许可证
├── requirements.txt                   # 依赖列表
├── config.json                        # 配置文件（需自行创建）
├── config.example.json                # 配置示例
│
├── data/                              # 数据文件
│   ├── weibo_final.json              # 微博数据（5960条）
│   ├── jike_posts_full.json          # 即刻数据（20条）
│   ├── persona_profile.json          # 人格档案
│   └── persona_profile_enhanced.json # 增强版人格档案（双模式）
│
├── core/                              # 核心模块
│   ├── content_generator.py          # 内容生成器
│   ├── persona_analyzer.py           # 人格分析器
│   └── privacy_checker.py            # 隐私检查（待实现）
│
├── adapters/                          # 平台适配器
│   └── jike/                         # 即刻适配器
│       ├── jike_v4.py                # 主脚本：登录+发帖
│       ├── jike_login_v3.py          # 登录模块
│       └── post_now_2026-04-19_v1.py # 单次发帖脚本
│
├── analysis/                          # 分析报告
│   ├── persona_insight.md            # 微博人格分析
│   ├── jike_interaction_analysis.md  # 即刻互动分析
│   └── generated_posts_from_memory_2026-04-17.json  # 生成的帖子
│
└── docs/                              # 文档
    ├── digital_persona_design.md     # 数字分身设计方案
    ├── jike_auto_operation_2026-03-19_v1.md  # 自动化方案
    └── project_retrospective_2026-04-22_v2.md # 项目复盘
```

---

## 技术方案

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Claw 数字分身系统                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   数据采集    │───→│   人格建模    │───→│   内容生成    │  │
│  │              │    │              │    │              │  │
│  │ • 微博爬虫   │    │ • 特征提取   │    │ • DeepSeek   │  │
│  │ • 即刻数据   │    │ • 双模式人格 │    │ • Prompt工程 │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│  ┌───────────────────────────────────────────────┘          │
│  │                                                          │
│  ▼                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   隐私检查    │───→│   人工确认    │───→│   自动发布    │  │
│  │              │    │              │    │              │  │
│  │ • 敏感信息   │    │ • 内容预览   │    │ • Playwright │  │
│  │ • 脱敏规则   │    │ • 用户批准   │    │ • Token持久化│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 核心技术栈

| 技术 | 用途 | 版本 |
|------|------|------|
| Python | 主语言 | 3.9+ |
| Playwright | 浏览器自动化 | 1.40+ |
| DeepSeek API | 内容生成 | v1 |
| JSON | 数据存储 | - |

### 关键设计决策

#### 1. 浏览器自动化 vs API 调用

**选择**: Playwright 浏览器自动化

**原因**:
- 即刻 API 有防护，直接调用返回 503
- 浏览器自动化成功率更高
- 模拟真实用户行为，降低被封风险

**实现**:
```python
# Token 持久化方案
扫码登录 → 提取 localStorage Token → 保存 → 下次注入自动登录
```

#### 2. 双模式人格

**工作模式**:
- 语气：专业、简洁、有条理
- 时段：工作日 9:00-18:00
- 内容：产品设计、行业观点

**生活模式**:
- 语气：轻松、幽默、随性
- 时段：晚间 20:00-凌晨 1:00
- 内容：生活观察、读书分享

#### 3. 隐私保护

**隐私边界**:
- ❌ 禁止：真实姓名、手机号、地址、公司名
- ✅ 允许：兴趣偏好、专业观点、生活经历（模糊化）

**脱敏规则**:
```python
sensitive_patterns = [
    (r'\d{17}[\dXx]', '[已脱敏]'),      # 身份证
    (r'1[3-9]\d{9}', '[已脱敏]'),       # 手机号
    (r'[\u4e00-\u9fa5]{2,}(路|街|号)', '[地址]'),  # 地址
]
```

#### 4. 内容生成策略

**基于真实记忆**:
- 使用真实读过的书（《古拉格群岛》《战后欧洲史》）
- 引用真实说过的话
- 结合真实职业经历

**Prompt 工程**:
```
你是 PrettyHugo，以下是你的真实背景...
【真实背景】
- 腾讯前产品经理，有总监级管理经验
- 真实读过的书：...
- 最近在做：...

【写作风格要求】
- 简洁克制，句号收尾
- 中英文混用
- 结尾必须加 (｡･ω･ａ)ﾉ♡
```

---

## 实践案例

### 我的实现路径

**1. 数据采集阶段**
- 爬取 14 年微博数据（5960 条）
- 分析互动模式、话题偏好、表达习惯
- 提取关键特征：简洁克制、中英文混用、善用"哈哈"

**2. 人格建模阶段**
- 构建双模式人格档案
- 工作模式：专业、理性、产品视角
- 生活模式：轻松、幽默、感性表达

**3. 内容生成阶段**
- 基于真实记忆生成内容
- 爆款案例：极狐阿尔法S华为HI自动驾驶体验（24742赞）
- 读书联想：《古拉格群岛》与推荐算法的思辨

**4. 自动化运营阶段**
- 即刻首帖已发，Token 持久化方案稳定
- 内容需人工确认后发布，风险控制到位

### 运营数据

| 指标 | 数值 |
|------|------|
| 微博数据 | 5960 条 |
| 即刻历史动态 | 20 条 |
| 微博最高赞 | 24,742 |
| 即刻粉丝 | 53 |

### 关键洞察

- **高互动话题**：旅行/户外 > 此刻的天空 > 产品思考
- **最佳时段**：工作日 12:00-12:30，晚间 19:00-21:00
- **内容策略**：图片内容互动率 +167%

---

## TODO

### P0 - 核心功能

- [ ] **图片上传**：Playwright 模拟文件选择，支持带图发帖
- [ ] **定时调度**：APScheduler 实现每天 12:00/20:00 自动发帖
- [ ] **豆瓣数据**：爬取书影音记录，丰富内容素材
- [ ] **Token 刷新**：自动刷新过期 Token

### P1 - 互动功能

- [ ] **自动评论**：浏览推荐内容，生成并发布评论
- [ ] **点赞功能**：自动点赞感兴趣的内容
- [ ] **关注用户**：基于话题匹配自动关注
- [ ] **通知处理**：自动处理评论回复、点赞通知

### P2 - 扩展优化

- [ ] **小红书适配器**：扩展到小红书平台
- [ ] **模块化重构**：将脚本拆分为独立模块
- [ ] **Web 管理界面**：可视化配置和监控
- [ ] **数据库存储**：从 JSON 迁移到 SQLite/PostgreSQL
- [ ] **内容效果分析**：基于互动数据优化生成策略

### P3 - 长期规划

- [ ] **多平台协同**：即刻 + 小红书 + 微博同步运营
- [ ] **智能进化**：基于反馈自动调整人格特征
- [ ] **语音/视频内容**：扩展到多媒体形式

---

## 贡献指南

欢迎提交 Issue 和 PR！

### 提交规范

- 使用 [Conventional Commits](https://conventionalcommits.org/)
- 代码风格遵循 PEP 8
- 新增功能需补充文档

### 开发流程

```bash
# 1. Fork 项目
# 2. 创建分支
git checkout -b feature/your-feature

# 3. 提交更改
git commit -m "feat: add some feature"

# 4. 推送分支
git push origin feature/your-feature

# 5. 创建 Pull Request
```

---

## 许可证

[MIT License](LICENSE)

---

## 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [DeepSeek](https://deepseek.com/) - AI 内容生成
- [即刻](https://okjike.com/) - 运营平台

---

*Made with ❤️ by [@PrettyHugo](https://weibo.com/prettyhugo)*
