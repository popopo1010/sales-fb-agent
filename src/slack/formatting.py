"""FB本文のSlack用フォーマット変換"""

import re


def format_feedback_for_slack(text: str) -> str:
    """FBの視認性向上：項目間の空行・各項目内の改行を正規化"""
    result = text
    result = re.sub(r"(### 全体評価：[\d\-]/10点)\s*", r"\1\n\n", result)
    result = re.sub(r"\n+(### \d+\.)", r"\n\n\n\1", result)
    result = re.sub(r"(### \d+\.[^\n]*)(\n)(?=[^\n])", r"\1\n\n", result)
    result = re.sub(r"([。])\s*([・\-]\s+)", r"\1\n\2", result)
    result = re.sub(r"([。）)])\s*([・·•①②③④⑤⑥⑦⑧⑨⑩])", r"\1\n\2", result)
    result = re.sub(r"([。】])\s*(-\s+)", r"\1\n\2", result)
    result = re.sub(r"(^[・\-]\s+[^\n]+)(\n)(?=[^・\-])", r"\1\n\n", result, flags=re.MULTILINE)
    return result.strip()


def markdown_to_plain(text: str) -> str:
    """Markdownをプレーンテキストに変換（Slack用）"""
    result = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    result = re.sub(r"\*\*(.+?)\*\*", r"\1", result)
    result = re.sub(r"__(.+?)__", r"\1", result)
    result = re.sub(r"\*(.+?)\*", r"\1", result)
    result = re.sub(r"_(.+?)_", r"\1", result)
    result = re.sub(r"^[\-\*]\s+", "・ ", result, flags=re.MULTILINE)
    return result


def force_line_breaks(text: str) -> str:
    """・や①②③の前で改行を強制"""
    result = re.sub(r"([^\n])([・·•]\s+)", r"\1\n\2", text)
    result = re.sub(r"([。）)])\s*([①②③④⑤⑥⑦⑧⑨⑩])", r"\1\n\2", result)
    result = re.sub(r"(点|不足|必要|ある|整理)\s*([・·•])\s*", r"\1\n\2 ", result)
    return result


def format_feedback_to_plain(text: str) -> str:
    """FB本文をSlack送信用プレーンテキストに変換（一連の処理）"""
    formatted = format_feedback_for_slack(text)
    plain = markdown_to_plain(formatted)
    return force_line_breaks(plain)
