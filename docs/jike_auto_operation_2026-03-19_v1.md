# 即刻账号自动化运营方案

> 版本: v1.0  
> 创建时间: 2026-03-19 19:35  
> 目标: 实现即刻账号完全自动化运营

---

## 一、现状分析

### 1.1 已有资源

| 资源 | 状态 | 说明 |
|------|------|------|
| **Token** | ✅ 有效 | JWT格式，可获取用户信息 |
| **内容计划** | ✅ 就绪 | 月度8篇帖子计划 |
| **数字分身设计** | ✅ 完成 | 工作模式+生活模式双人格 |
| **API域名** | ⚠️ 已知 | `web-api.okjike.com`（返回503） |
| **浏览器自动化** | ⚠️ 部分可用 | 可打开浏览器、登录，但发帖未完成 |

### 1.2 未打通功能

| 功能 | API状态 | 浏览器自动化状态 | 优先级 |
|------|---------|------------------|--------|
| 发布帖子 | ❌ 未找到 | ⚠️ 部分可用 | P0 |
| 发布评论 | ❌ 未找到 | ❌ 未实现 | P1 |
| 点赞 | ❌ 未找到 | ❌ 未实现 | P1 |
| 关注用户 | ❌ 未找到 | ❌ 未实现 | P2 |
| 获取推荐内容 | ❌ 未找到 | ❌ 未实现 | P1 |
| 获取通知 | ❌ 未找到 | ❌ 未实现 | P1 |

---

## 二、技术方案

### 2.1 混合策略

```
┌─────────────────────────────────────────────────────────┐
│                  即刻自动化运营系统                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  API优先方案  │         │ 浏览器备选方案 │             │
│  │              │         │              │             │
│  │ - 速度快     │         │ - 成功率高   │             │
│  │ - 稳定性好   │         │ - 无需API    │             │
│  │ - 可批量操作 │         │ - 可处理验证 │             │
│  └──────┬───────┘         └──────┬───────┘             │
│         │                        │                      │
│         └────────────┬───────────┘                      │
│                      │                                  │
│              ┌───────▼───────┐                          │
│              │  统一调度层   │                          │
│              └───────┬───────┘                          │
│                      │                                  │
│         ┌────────────┴────────────┐                    │
│         │                         │                    │
│  ┌──────▼──────┐          ┌──────▼──────┐             │
│  │  内容生成    │          │  互动引擎    │             │
│  └─────────────┘          └─────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 方案对比

| 维度 | API方案 | 浏览器自动化方案 |
|------|---------|------------------|
| **开发难度** | 高（需要逆向） | 中（需要调试选择器） |
| **稳定性** | 高（标准HTTP） | 中（依赖页面结构） |
| **速度** | 快（毫秒级） | 慢（秒级） |
| **维护成本** | 低（API稳定） | 高（页面变化需更新） |
| **风险** | API变更 | 反爬虫、验证码 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 三、实施计划

### 3.1 第一阶段：浏览器自动化（本周）

**目标**：通过浏览器自动化实现基础发帖功能

**任务列表**：

- [x] 打开浏览器并登录（已完成）
- [ ] 完善发帖功能（需调试选择器）
- [ ] 实现评论功能
- [ ] 实现点赞功能
- [ ] 实现关注功能

**预期时间**：2-3天

### 3.2 第二阶段：API逆向研究（持续进行）

**目标**：通过抓包找到真实的API端点

**方法**：

1. **手动抓包**
   - 使用浏览器开发者工具
   - 在即刻Web版进行各种操作
   - 捕获并分析请求

2. **自动化拦截**
   - 使用Playwright拦截请求
   - 在自动化操作时捕获
   - 建立API文档

3. **社区研究**
   - GitHub搜索相关项目
   - 技术博客和论坛
   - 即刻API相关讨论

**关键数据**：

- 发布帖子的API端点
- 请求头格式（特别是认证方式）
- 请求体格式
- 图片上传方式

### 3.3 第三阶段：完整自动化运营（下周）

**目标**：实现完全自动化的内容发布和互动

**功能模块**：

```
jike_auto_operation/
├── core/
│   ├── browser_automation.py  # 浏览器自动化核心
│   ├── api_client.py          # API客户端（待开发）
│   └── scheduler.py           # 调度器
│
├── content/
│   ├── generator.py           # 内容生成
│   ├── image_handler.py       # 图片处理
│   └── persona.py             # 人格引擎
│
├── interaction/
│   ├── commenter.py           # 评论管理
│   ├── liker.py               # 点赞管理
│   └── follower.py            # 关注管理
│
└── config/
    ├── settings.py            # 配置文件
    └── persona_config.json    # 人格配置
```

---

## 四、核心模块设计

### 4.1 浏览器自动化核心

```python
class JikeBrowserAutomation:
    """即刻浏览器自动化"""
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.logged_in = False
    
    async def initialize(self):
        """初始化浏览器"""
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        # 注入token登录
        await self._inject_token()
    
    async def _inject_token(self):
        """注入token实现自动登录"""
        # 设置localStorage中的token
        await self.page.goto('https://web.okjike.com')
        await self.page.evaluate(f'''
            localStorage.setItem('jike-access-token', '{self.token}');
        ''')
        await self.page.reload()
        self.logged_in = True
    
    async def create_post(self, content: str, images: list = None, topic: str = None):
        """发布帖子"""
        # 实现发帖逻辑
        pass
    
    async def comment(self, post_id: str, content: str):
        """发布评论"""
        pass
    
    async def like(self, post_id: str):
        """点赞"""
        pass
    
    async def follow(self, user_id: str):
        """关注用户"""
        pass
```

### 4.2 内容生成器

```python
class ContentGenerator:
    """内容生成器"""
    
    def __init__(self, persona_config):
        self.persona = persona_config
        self.topics = ["此刻的天空", "产品思考", "生活观察"]
    
    def generate_post(self, topic: str = None, length: str = "80-120字"):
        """生成帖子内容"""
        # 基于人格配置生成内容
        # 返回：(内容, 需要确认)
        pass
    
    def generate_comment(self, post_content: str, post_topic: str):
        """生成评论"""
        # 基于帖子内容和话题生成评论
        pass
```

### 4.3 调度器

```python
class JikeScheduler:
    """即刻运营调度器"""
    
    def __init__(self):
        self.browser = JikeBrowserAutomation()
        self.generator = ContentGenerator()
        self.content_plan = self._load_content_plan()
    
    async def run_daily_tasks(self):
        """执行每日任务"""
        # 1. 检查今日是否有发布计划
        # 2. 生成内容并确认
        # 3. 发布帖子
        # 4. 浏览推荐内容
        # 5. 进行互动（评论、点赞）
        pass
    
    async def publish_scheduled_post(self):
        """发布计划的帖子"""
        pass
    
    async def browse_and_interact(self):
        """浏览并互动"""
        pass
```

---

## 五、隐私和安全

### 5.1 隐私保护

- **内容脱敏**：发布前检查敏感信息
- **人格隔离**：数字分身与真实身份隔离
- **人工确认**：前期所有操作需要确认

### 5.2 风险控制

- **频率限制**：避免过于频繁的操作
- **异常处理**：遇到验证码或错误时的处理
- **日志记录**：记录所有操作，便于追溯

---

## 六、下一步行动

### 立即执行

1. **完善浏览器自动化发帖功能**
   - 调试选择器
   - 实现图片上传
   - 实现话题选择

2. **运行第一次自动化发帖测试**
   - 准备测试内容
   - 执行发帖
   - 验证结果

### 本周目标

- [ ] 实现浏览器自动化发帖
- [ ] 完成第一篇自动化发布的帖子
- [ ] 实现评论和点赞功能
- [ ] 建立基础的内容生成流程

---

*文档版本: v1.0 | 创建时间: 2026-03-19 19:35*
