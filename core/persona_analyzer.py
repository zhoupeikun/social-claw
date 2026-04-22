#!/usr/bin/env python3
"""
微博人格分析脚本 v2
过滤系统消息,提取真实人格特征
"""

import json
import re
from collections import Counter

def load_weibo_data():
    """加载微博数据"""
    with open('weibo_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_system_messages(texts):
    """过滤微博系统消息,保留真实内容"""
    system_patterns = [
        r'^抱歉',
        r'^根据作者设置',
        r'^此微博已不可见',
        r'^此微博已被作者删除',
        r'^该内容请至手机客户端查看',
        r'^查看二维码',
        r'^查看帮助',
        r'^现已无法查看',
        r'^微博社区公约',
        r'^该账号因被投诉',
        r'^转发微博$',
        r'^网页链接$',
        r'^客户端$',
        r'^长图$',
        r'^\s*$',
    ]
    
    filtered = []
    for text in texts:
        # 检查是否是系统消息
        is_system = False
        for pattern in system_patterns:
            if re.match(pattern, text.strip()):
                is_system = True
                break
        
        if not is_system and len(text.strip()) > 10:
            filtered.append(text)
    
    return filtered

def extract_real_content(weibo_data):
    """提取真实微博内容"""
    real_contents = []
    
    for w in weibo_data:
        text = w.get('text', '')
        
        # 分割多条微博内容 (以日期开头)
        parts = re.split(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', text)
        
        for part in parts:
            # 清理系统消息
            part = re.sub(r'来自[^\s]+', '', part)  # 移除来源
            part = re.sub(r'阅读\s*推广', '', part)  # 移除阅读推广
            part = re.sub(r'\d+\s*转发', '', part)  # 移除转发数
            part = re.sub(r'\d+\s*评论', '', part)  # 移除评论数
            part = re.sub(r'网页链接', '', part)
            part = re.sub(r'客户端', '', part)
            part = re.sub(r'长图', '', part)
            part = re.sub(r'展开\s*全文', '', part)
            part = re.sub(r'抱歉，.*?。', '', part)
            part = re.sub(r'根据作者设置的微博可见时间范围.*?。', '', part)
            part = re.sub(r'此微博已不可见', '', part)
            part = re.sub(r'此微博已被作者删除', '', part)
            part = re.sub(r'该内容请至手机客户端查看', '', part)
            part = re.sub(r'查看二维码', '', part)
            part = re.sub(r'查看帮助', '', part)
            part = re.sub(r'现已无法查看', '', part)
            part = re.sub(r'微博社区公约.*?。', '', part)
            part = re.sub(r'该账号因被投诉.*?。', '', part)
            
            part = part.strip()
            if len(part) > 15:  # 过滤太短的内容
                real_contents.append(part)
    
    return real_contents

def analyze_persona(weibo_data):
    """分析人格特征"""
    
    # 提取真实内容
    print("🔍 过滤系统消息...")
    real_contents = extract_real_content(weibo_data)
    print(f"✅ 提取到 {len(real_contents)} 条真实内容")
    
    all_text = ' '.join(real_contents)
    
    # 1. 高频词汇分析
    stopwords = {
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', '他', '她', '它', '们', '这个', '那个', '但是', '因为', '所以', '如果', '还是', '可以', '可能', '应该', '已经', '一下', '一些', '一直', '一点', '真是', '真的', '感觉', '觉得', '知道', '以为', '发现', '虽然', '不过', '现在', '今天', '明天', '昨天', '然后', '这样', '那样', '这么', '那么', '怎么', '为什么', '哪里', '那里', '这里', '转发', '评论', '微博', '来自', '阅读', '推广', '展开', '全文', '还有', '就是', '不是', '这种', '那种', '或者', '而且', '只能', '已经', '还是', '也是', '都是', '更是', '只是', '都是', '比较', '特别', '非常', '相当', '更加', '最为', '其', '之', '与', '及', '等', '等等', '把', '被', '让', '给', '向', '从', '对', '又', '再', '也', '还', '都', '才', '只', '仅', '最', '更', '很', '太', '好', '多', '少', '大', '小', '高', '低', '长', '短', '快', '慢', '早', '晚', '前', '后', '左', '右', '上', '下', '中', '内', '外', '里', '边', '面', '头', '尾', '始', '终', '先', '后',
    }
    
    # 提取中文词组
    words = re.findall(r'[\u4e00-\u9fa5]{2,4}', all_text)
    words = [w for w in words if w not in stopwords and not w.isdigit()]
    
    word_freq = Counter(words).most_common(50)
    
    # 2. 话题标签
    topics = re.findall(r'#([^#]+)#', all_text)
    topic_freq = Counter(topics).most_common(20)
    
    # 3. @ 提及
    mentions = re.findall(r'@([^\s@:：,，。！？]+)', all_text)
    mention_freq = Counter(mentions).most_common(15)
    
    # 4. 表情符号
    emojis = re.findall(r'[\U0001F300-\U0001F9FF]', all_text)
    emoji_freq = Counter(emojis).most_common(10)
    
    # 5. 情感词分析
    positive_words = ['好', '喜欢', '赞', '棒', '厉害', '优秀', '精彩', '美好', '开心', '快乐', '幸福', '感谢', '谢谢', '支持', '期待', '希望', '爱']
    negative_words = ['不', '没', '差', '烂', '坑', '烦', '累', '苦', '怒', '恨', '骂', '讨厌', '恶心', '无语', '失望', '遗憾', '可惜']
    
    positive_count = sum(1 for w in words if any(pw in w for pw in positive_words))
    negative_count = sum(1 for w in words if any(nw in w for nw in negative_words))
    
    # 6. 时间词分析
    time_words = ['今天', '昨天', '明天', '今年', '去年', '明年', '早上', '晚上', '中午', '下午', '周末', '假期']
    time_mentions = {tw: all_text.count(tw) for tw in time_words if all_text.count(tw) > 0}
    
    # 7. 常见句式
    sentences = []
    for text in real_contents:
        sents = re.split(r'[。！？\n]', text)
        sentences.extend([s.strip() for s in sents if 10 < len(s.strip()) < 100])
    
    # 提取开头
    sentence_starts = [s[:15] for s in sentences if len(s) >= 15]
    start_freq = Counter(sentence_starts).most_common(15)
    
    # 8. 内容分类
    categories = {
        '科技数码': ['手机', '华为', '苹果', '安卓', '电脑', '软件', 'APP', '系统', '小米', '荣耀'],
        '生活日常': ['吃饭', '睡觉', '上班', '下班', '周末', '今天', '明天', '朋友', '家人'],
        '观点评论': ['觉得', '认为', '感觉', '应该', '支持', '反对', '觉得', '看来'],
        '转发分享': ['//@', '转发', '分享', '推荐'],
        '情感表达': ['哈哈', '呵呵', '唉', '无语', '醉了', '喜欢', '讨厌'],
    }
    
    category_counts = {}
    for cat, keywords in categories.items():
        count = sum(all_text.count(kw) for kw in keywords)
        category_counts[cat] = count
    
    return {
        'word_freq': word_freq,
        'topic_freq': topic_freq,
        'mention_freq': mention_freq,
        'emoji_freq': emoji_freq,
        'positive_ratio': positive_count / max(positive_count + negative_count, 1),
        'time_mentions': time_mentions,
        'sentence_starts': start_freq,
        'category_counts': category_counts,
        'total_real_contents': len(real_contents),
        'avg_length': len(all_text) / len(real_contents) if real_contents else 0,
    }


def generate_persona_report(analysis):
    """生成人格报告"""
    
    report = {
        'summary': {
            'content_count': analysis['total_real_contents'],
            'avg_length': round(analysis['avg_length'], 1),
            'tone': '积极' if analysis['positive_ratio'] > 0.5 else '中性',
        },
        'keywords': {
            'top_words': [w[0] for w in analysis['word_freq'][:20]],
            'word_frequencies': dict(analysis['word_freq'][:30]),
        },
        'interests': {
            'topics': [t[0] for t in analysis['topic_freq'][:10]],
            'mentions': [m[0] for m in analysis['mention_freq'][:10]],
        },
        'communication_style': {
            'common_opens': [s[0] for s in analysis['sentence_starts'][:10]],
            'emojis': [e[0] for e in analysis['emoji_freq'][:5]],
        },
        'content_categories': analysis['category_counts'],
        'time_patterns': analysis['time_mentions'],
        'persona_description': '',
    }
    
    # 生成人格描述
    top_words = '、'.join([w[0] for w in analysis['word_freq'][:8]])
    top_categories = sorted(analysis['category_counts'].items(), key=lambda x: x[1], reverse=True)[:3]
    categories_str = '、'.join([c[0] for c in top_categories])
    
    report['persona_description'] = f"""
## 🦞 PrettyHugo 数字分身人格档案

### 基本信息
- 微博数量: {analysis['total_real_contents']} 条有效内容
- 平均长度: {analysis['avg_length']:.0f} 字/条
- 语言风格: {'积极向上' if analysis['positive_ratio'] > 0.6 else '理性客观' if analysis['positive_ratio'] > 0.4 else '冷静内敛'}

### 语言特征
- 高频词汇: {top_words}
- 常用话题: {', '.join([t[0] for t in analysis['topic_freq'][:5]]) if analysis['topic_freq'] else '无特定话题'}
- 典型开头: {analysis['sentence_starts'][0][0] if analysis['sentence_starts'] else '无'}

### 兴趣领域
- 主要关注: {categories_str}
- 常互动对象: {', '.join([m[0] for m in analysis['mention_freq'][:5]]) if analysis['mention_freq'] else '无'}

### 表达风格
- 善于表达观点和看法
- 关注科技数码领域
- 有自己的生活态度和价值观
""".strip()
    
    return report


def main():
    print("🦞 Claw 人格分析器 v2")
    print("=" * 50)
    
    # 加载数据
    print("📂 加载微博数据...")
    weibo_data = load_weibo_data()
    print(f"✅ 共 {len(weibo_data)} 条微博")
    
    # 分析
    print("\n🔍 分析人格特征...")
    analysis = analyze_persona(weibo_data)
    
    # 打印结果
    print("\n📊 分析结果:")
    print(f"\n1️⃣ 有效内容: {analysis['total_real_contents']} 条")
    print(f"   平均长度: {analysis['avg_length']:.1f} 字")
    print(f"   积极情绪占比: {analysis['positive_ratio']*100:.1f}%")
    
    print(f"\n2️⃣ 高频词汇 (前 15):")
    for word, count in analysis['word_freq'][:15]:
        print(f"   {word}: {count}")
    
    print(f"\n3️⃣ 内容分类:")
    for cat, count in sorted(analysis['category_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    print(f"\n4️⃣ 常用话题:")
    for topic, count in analysis['topic_freq'][:10]:
        print(f"   #{topic}#: {count}")
    
    # 生成报告
    print("\n📝 生成人格报告...")
    report = generate_persona_report(analysis)
    
    # 保存报告
    with open('persona_profile.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("✅ 人格档案已保存到: persona_profile.json")
    
    # 打印人格描述
    print("\n" + "=" * 50)
    print(report['persona_description'])


if __name__ == "__main__":
    main()
