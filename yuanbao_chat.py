import requests
import json
from typing import Tuple, List

import utils.user_agents as user_agents


def merge_thoughts(thoughts: List[str]) -> str:
    """
    合并思考片段为完整文本

    Args:
        thoughts (List[str]): 思考片段列表

    Returns:
        str: 合并后的完整思考文本
    """
    merged_thoughts = []
    current_thought = ""

    for thought in thoughts:
        if thought:
            if len(thought.strip()) <= 2:  # 如果是短片段
                current_thought += thought
            else:
                if current_thought:  # 如果有累积的短片段
                    merged_thoughts.append(current_thought)
                    current_thought = ""
                merged_thoughts.append(thought)

    if current_thought:  # 添加最后剩余的短片段
        merged_thoughts.append(current_thought)

    merged = " ".join(thought.strip() for thought in merged_thoughts if thought.strip())
    return merged if merged else "null"


def chat_with_yuanbao(
    cookie: str, # 用户认证Cookie
    uuid: str, # 会话UUID
    message: str, # 要发送的消息内容
    model: str = "v3", # 模型类型，"v3"或"r1"，默认为"v3"
    internet: bool = False # 是否使用互联网搜索功能，默认为True

) -> Tuple[str, str]:
    """
    与腾讯元宝API交互的封装函数

    Args:
        cookie (str): 用户认证Cookie
        uuid (str): 会话UUID
        message (str): 要发送的消息内容
        model (str): 模型类型，"v3"或"r1"，默认为"v3"

    Returns:
        Tuple[str, str]:
            - 第一个字符串是合并后的完整思考过程
            - 第二个字符串是合并后的完整输出内容
    """
    url = f"https://yuanbao.tencent.com/api/chat/{uuid}"

    headers = {
        "Content-Type": "application/json", 
        "Cookie": cookie,
        "User-Agent": user_agents.get_random_user_agent()  # 使用随机User-Agent
        }

    # 根据model参数设置默认为v3
    model_mapping = {
        "deep_seek_v3": "deep_seek_v3",
        "deep_seek_r1": "deep_seek",
        "hunyuan": "hunyuan_gpt_175B_0404",
        "hunyuan_t1": "hunyuan_t1"
    }
    chat_model_id = model_mapping.get(model, "deep_seek_v3")  # 默认使用v3模型
    # 检查是否使用互联网搜索功能
    support_functions = ["supportInternetSearch"] if internet else []

    payload = {
        "model": "gpt_175B_0404",
        "prompt": message,
        "plugin": "Adaptive",
        "displayPrompt": message,
        "displayPromptType": 1,
        "options": {
            "imageIntention": {
                "needIntentionModel": True,
                "backendUpdateFlag": 2,
                "intentionStatus": True,
            }
        },
        "multimedia": [],
        "agentId": "naQivTmsDa",
        "supportHint": 1,
        "version": "v2",
        "chatModelId": chat_model_id,  # 设置聊天模型ID
        "supportFunctions": support_functions,  # 是否支持互联网搜索功能
    }

    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            thinking_process = []
            final_output = []

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8").strip()

                    if line_str.startswith("data: "):
                        json_str = line_str[6:]

                        if json_str in ["status", "reasoner", "text"] or (
                            json_str.startswith("[") and json_str.endswith("]")
                        ):
                            continue

                        try:
                            data = json.loads(json_str)
                            if data.get("type") == "think":
                                thinking_process.append(data.get("content", ""))
                            elif data.get("type") == "text" and data.get("msg"):
                                final_output.append(data["msg"])
                            elif data.get("content"):
                                final_output.append(data["content"])
                        except json.JSONDecodeError:
                            continue

            # 合并思考过程和输出内容
            merged_thinking = merge_thoughts(thinking_process)
            merged_output = "".join(final_output)

            return merged_thinking, merged_output

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return "", ""


def print_chat_result(thinking: str, output: str) -> None:
    """
    打印聊天结果

    Args:
        thinking (str): 完整的思考过程
        output (str): 完整的输出内容
    """
    if thinking:
        print("\n思考过程:")
        print(thinking)

    if output:
        print("\n最终回答:")
        print(output)
