import os
from typing import Optional

from dotenv import load_dotenv


MODEL_ENV = "DASHSCOPE_MODEL"
API_KEY_ENV = "DASHSCOPE_API_KEY"
DEFAULT_MODEL = "qwen-turbo"
DEFAULT_GOAL = "exam"
DEFAULT_SCENARIO = "self_study"

GOAL_OPTIONS = [
    {
        "value": "exam",
        "label": "考前冲刺",
        "description": "优先提炼高频考点、易错点和速记内容。",
        "focus": "优先保留考试高频概念、定义、分类、步骤、机制、结论与易错点。",
        "format_instructions": (
            "请严格按以下结构输出：\n"
            "一、主题概览\n"
            "- 用 1-2 句话概括这份资料主要讲什么。\n\n"
            "二、高优先级考点\n"
            "- 提炼 5-8 条最值得复习的考点；\n"
            "- 每条包含：考点名称 + 简要解释 + 为什么值得重点复习。\n\n"
            "三、易错/易混淆点\n"
            "- 列出 2-4 条容易混淆、遗漏或混为一谈的内容。\n\n"
            "四、考前速记\n"
            "- 用 3-5 条短句总结最后冲刺时最该记住的内容。"
        ),
    },
    {
        "value": "understand",
        "label": "入门理解",
        "description": "更重视概念解释、逻辑关系和基础理解。",
        "focus": "更重视概念解释、前后逻辑、因果关系、关键术语和理解门槛高的部分。",
        "format_instructions": (
            "请严格按以下结构输出：\n"
            "一、这份资料在讲什么\n"
            "- 用通俗的 1-2 句话概括主题。\n\n"
            "二、核心概念拆解\n"
            "- 提炼 4-6 个核心概念；\n"
            "- 每条包含：概念名称 + 通俗解释 + 与主题的关系。\n\n"
            "三、逻辑主线\n"
            "- 按顺序说明资料的核心逻辑、步骤或因果关系。\n\n"
            "四、容易卡住的点\n"
            "- 列出 2-4 个初学者最可能不理解的地方，并简要提示如何理解。"
        ),
    },
    {
        "value": "teach",
        "label": "授课备课",
        "description": "强调讲解顺序、重点难点和课堂表达。",
        "focus": "更重视讲解结构、重点难点、课堂表达顺序以及适合讲给别人听的组织方式。",
        "format_instructions": (
            "请严格按以下结构输出：\n"
            "一、授课主题概览\n"
            "- 用 1-2 句话说明本节内容的核心主题。\n\n"
            "二、讲解主线\n"
            "- 按适合讲解的顺序整理 4-6 个主要模块。\n\n"
            "三、重点与难点\n"
            "- 分别列出最值得强调的重点和学生可能难理解的难点。\n\n"
            "四、课堂提示\n"
            "- 给出 3-5 条适合讲课时提醒学生注意的内容；\n"
            "- 如果原文缺少案例或例子，明确写“原文未提供实例”。"
        ),
    },
]

SCENARIO_OPTIONS = [
    {
        "value": "self_study",
        "label": "自主复习",
        "description": "输出紧凑，适合自己快速过一遍。",
        "style_instruction": "输出要紧凑、直接，便于个人快速复习和查漏补缺。",
    },
    {
        "value": "preview_review",
        "label": "课前预习/课后复盘",
        "description": "先建立框架，再定位待重点消化内容。",
        "style_instruction": "先帮助用户建立整体框架，再提示课前重点关注或课后需要回看的部分。",
    },
    {
        "value": "note_taking",
        "label": "整理笔记",
        "description": "更像可直接保存的结构化学习笔记。",
        "style_instruction": "输出要像一份可直接保存的结构化笔记，层级分明、表述克制、不口语化。",
    },
    {
        "value": "sharing",
        "label": "讲解分享",
        "description": "适合向同学或团队复述和讲解。",
        "style_instruction": "输出要照顾向他人讲解的场景，层次清楚、衔接自然，方便复述。",
    },
]


load_dotenv()


def _get_generation_client():
    # Delay importing dashscope until a real summarize request happens.
    from dashscope import Generation

    return Generation


def _get_option(options, value: Optional[str], default_value: str):
    mapping = {item["value"]: item for item in options}
    return mapping.get(value) or mapping[default_value]


def resolve_summary_mode(goal: Optional[str], scenario: Optional[str]):
    goal_option = _get_option(GOAL_OPTIONS, goal, DEFAULT_GOAL)
    scenario_option = _get_option(SCENARIO_OPTIONS, scenario, DEFAULT_SCENARIO)
    return goal_option, scenario_option


def _pick_content(response) -> Optional[str]:
    """Attempt to read text content from dashscope response."""
    if not response:
        return None
    output = getattr(response, "output", None)
    if output is None:
        return None
    # Newer SDKs may expose output.text directly.
    text = getattr(output, "text", None)
    if text:
        return text
    # Fallback to choices[0].message.content
    try:
        return output.choices[0]["message"]["content"]
    except Exception:
        return None


def summarize_text(
    raw_text: str,
    *,
    goal: str = DEFAULT_GOAL,
    scenario: str = DEFAULT_SCENARIO,
    max_chars: int = 12000,
) -> str:
    """
    Call DashScope to summarize extracted PDF text.
    Trims input to max_chars to control latency and token usage.
    """
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置，请在 .env 中设置后重试")

    model = os.getenv(MODEL_ENV, DEFAULT_MODEL)
    trimmed = raw_text[:max_chars]
    goal_option, scenario_option = resolve_summary_mode(goal, scenario)

    system_prompt = (
        "你是一名面向学习场景的 AI 学习助手，擅长从课程讲义、教材节选和复习资料中提炼结构化知识。"
        "你的目标不是泛泛总结，而是根据用户目标和使用场景，生成更适合实际使用的学习材料。"
        "你必须严格遵守以下规则："
        "1. 只能依据用户提供的文本总结，不补充原文未提及的事实；"
        "2. 输出使用中文；"
        "3. 忽略明显的页码、页眉页脚、重复段落和错乱换行；"
        "4. 不要大段照抄原文，不要输出空泛套话；"
        "5. 如果原文信息不足，请明确写“原文未明确说明”。"
    )
    user_prompt = (
        f"用户目标：{goal_option['label']}\n"
        f"使用场景：{scenario_option['label']}\n"
        f"目标侧重点：{goal_option['focus']}\n"
        f"场景表达要求：{scenario_option['style_instruction']}\n\n"
        "下面的内容来自 PDF 文本抽取，可能存在换行错乱、重复片段或格式噪声。\n"
        "请输出一份真正适合该用户目标和使用场景的总结结果，而不是套用单一模板。\n\n"
        f"{goal_option['format_instructions']}\n\n"
        "额外要求：\n"
        "- 只保留对当前目标和场景真正有帮助的信息；\n"
        "- 能明确写定义、分类、流程、结论时就不要泛化成空话；\n"
        "- 如果某一部分没有足够依据，可以简要说明原文信息有限；\n\n"
        "原文如下：\n"
        "<document>\n"
        f"{trimmed}\n"
        "</document>"
    )

    generation_client = _get_generation_client()

    response = generation_client.call(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        api_key=api_key,
    )

    content = _pick_content(response)
    if not content:
        raise RuntimeError("模型返回为空，请稍后重试")
    return content.strip()
