#!/usr/bin/env python3
"""
即刻内容生成器
基于 PrettyHugo 人格档案自动生成帖子内容
"""
import json
import random
import re
from datetime import datetime
from pathlib import Path

PERSONA_FILE = Path(__file__).parent / "persona_profile_enhanced.json"
SECRET_SIGNAL = "(｡･ω･ａ)ﾉ♡"


def load_persona():
    """加载人格档案"""
    with open(PERSONA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mode(hour=None):
    """根据时间判断模式"""
    if hour is None:
        hour = datetime.now().hour
    persona = load_persona()
    if hour in persona["work_mode"]["active_hours"]:
        return "work"
    return "life"


def select_topic():
    """基于权重选择话题"""
    persona = load_persona()
    dist = persona["content_strategy"]["topic_distribution"]
    topics = list(dist.keys())
    weights = list(dist.values())
    chosen = random.choices(topics, weights=weights, k=1)[0]
    return chosen


# ===== LLM 内容生成提示词 =====
TOPIC_PROMPTS = {
    "此刻的天空": """分享一张此刻看到的天空照片或描述天空的状态。
要求：
- 简洁直接，像发朋友圈一样自然
- 可以带点情绪（舒服/发呆/治愈）
- 30-80字，不要太长
- 不要标题，不要序号
- 结尾加 {signal}""",

    "旅行记录": """分享一个你去过的地方，可以是旅行、出差、逛街偶遇。
要求：
- 有点细节，不要流水账
- 可以带点个人感受
- 50-100字
- 不要标题，不要序号
- 结尾加 {signal}""",

    "产品思考": """分享一个产品经理视角的思考，可以是：
- 对某个 App/功能的观察
- 用户体验的洞察
- 产品设计的点评
- 工作中的感悟
要求：
- 有观点，有具体例子
- 不要太长，一段话
- 80-150字
- 不要标题，不要序号
- 结尾加 {signal}""",

    "生活观察": """分享一个你在生活中观察到的小细节、小瞬间。
要求：
- 善于发现，有趣或有意思
- 简短，30-80字
- 自然，像即兴发的朋友圈
- 不要标题，不要序号
- 结尾加 {signal}""",

    "读书分享": """分享你最近读的一本书或一篇文章的感悟。
要求：
- 简短，一两句话
- 真实感受，不要过度推荐
- 30-80字
- 不要标题，不要序号
- 结尾加 {signal}""",
}


def build_llm_prompt(topic, mode):
    """构建发给 LLM 的提示词"""
    persona = load_persona()
    mode_data = persona[f"{mode}_mode"]

    topic_instruction = TOPIC_PROMPTS.get(
        topic,
        f"分享一个关于「{topic}」的内容。\n要求：自然真实，{mode_data['tone']}，50-100字，结尾加 {SECRET_SIGNAL}"
    ).replace("{signal}", SECRET_SIGNAL)

    system_prompt = f"""你是一个叫 PrettyHugo 的人，在即刻平台发帖。
你的风格是：{mode_data['tone']}
常用表达：{', '.join(mode_data['typical_expressions'])}
发微博的平均长度：约55字
你会用中文夹杂少量英文（bilingual）
emoji 使用适中（{mode_data['emoji_usage']}）
隐私规则：永远不提真实姓名、具体公司名、家庭信息。

现在请生成一条即刻帖子："""

    full_prompt = f"""{system_prompt}

{topic_instruction}

生成后检查：
1. 不含任何真实姓名/公司名/家庭信息
2. 长度符合要求
3. 风格自然，不要过于正式或像 AI 写的
4. 必须以 {SECRET_SIGNAL} 结尾"""
    return full_prompt


def call_llm(prompt):
    """
    调用 DeepSeek API 生成内容
    API 地址: https://api.deepseek.com/v1/chat/completions
    模型: deepseek-chat（擅长中文，性价比高）
    """
    import os
    import requests

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        # 尝试从配置文件读取
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_key = cfg.get("deepseek_api_key", "")

    if not api_key:
        raise EnvironmentError(
            "未找到 DEEPSEEK_API_KEY。\n"
            "请选择任一方式配置 API Key：\n"
            "1. 设置环境变量: export DEEPSEEK_API_KEY='your-key'\n"
            "2. 创建 Claw/config.json，内容: {\"deepseek_api_key\": \"your-key\"}\n"
            "  DeepSeek API Key 获取地址: https://platform.deepseek.com （控制台 → API Keys）"
        )

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,  # 有创意但不随机
            "max_tokens": 300,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LLM 调用失败: HTTP {response.status_code}\n{response.text[:200]}"
        )

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    # 去掉可能的 markdown 格式
    content = re.sub(r"^```(?:markdown)?\s*", "", content.strip())
    content = re.sub(r"\s*```$", "", content)
    return content


def generate_content(topic=None, mode=None, use_llm=True):
    """
    生成一条即刻帖子内容

    参数:
        topic: 指定话题，默认按权重随机
        mode: 'work' | 'life' | None（None根据时间自动判断）
        use_llm: True=调用LLM生成，False=返回prompt供手动测试

    返回:
        str: 帖子内容（已包含暗号）
    """
    if mode is None:
        mode = get_mode()

    if topic is None:
        topic = select_topic()

    prompt = build_llm_prompt(topic, mode)

    if use_llm:
        content = call_llm(prompt)
    else:
        # 调试模式：返回 prompt，供手动发给 LLM 测试
        print(f"=" * 60)
        print(f"话题: {topic} | 模式: {mode}")
        print(f"=" * 60)
        print(prompt)
        print(f"=" * 60)
        return prompt

    # 质量检查
    content = content.strip()
    assert SECRET_SIGNAL in content, "生成内容缺少发帖暗号！"
    assert len(content) <= 500, f"内容过长（{len(content)}字），请精简"

    # 隐私检查
    forbidden = ["周培坤", "真名", "我老婆", "我老公", "我女朋友", "我男朋友"]
    for word in forbidden:
        assert word not in content, f"内容含有隐私词汇: {word}"

    return content


# ===== 批量生成预览 =====
def preview_all_topics():
    """生成所有话题的 prompt 预览，用于快速验证内容质量"""
    print("=" * 60)
    print("所有话题 Prompt 预览（手动发给 LLM 测试）")
    print("=" * 60)
    for topic in TOPIC_PROMPTS.keys():
        print(f"\n### 话题: {topic}")
        mode = "work" if topic == "产品思考" else "life"
        prompt = build_llm_prompt(topic, mode)
        print(prompt)
        print("-" * 40)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_all_topics()
    else:
        # 随机选话题，按当前时间判断模式
        topic = select_topic()
        mode = get_mode()
        print(f"生成帖子 | 话题: {topic} | 模式: {mode}")
        print("-" * 40)
        try:
            content = generate_content(topic=topic, mode=mode, use_llm=True)
            print("=" * 50)
            print("生成结果:")
            print("=" * 50)
            print(content)
            print("=" * 50)
            print(f"字数: {len(content)}")
        except EnvironmentError as e:
            print(f"\n⚠️ {e}")
            print("\nDeepSeek API Key 获取方式:")
            print("  1. 打开 https://platform.deepseek.com")
            print("  2. 登录 → 点击右上角头像 → API Keys")
            print("  3. 创建新 Key，复制回来")
            print("\n配置方式（任选其一）:")
            print("  方式一: export DEEPSEEK_API_KEY='sk-xxxxxxxxxxxx'")
            print("  方式二: 创建 Claw/config.json:")
            print('         {"deepseek_api_key": "sk-xxxxxxxxxxxx"}')
