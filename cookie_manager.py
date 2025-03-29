import os
from venv import logger
import requests
import json
from typing import Optional, Dict, Any

import user_agents

def is_cookie_valid(cookie: str) -> bool:
    """
    测试cookie是否有效

    Args:
        cookie (str): 需要测试的cookie字符串

    Returns:
        bool: cookie有效返回True,否则返回False
    """
    test_url = "https://yuanbao.tencent.com/api/getuserinfo"
    headers = {
        "Cookie": cookie,
        "User-Agent": user_agents.get_random_user_agent()  # 使用user_agents库生成随机User-Agent
    }

    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # 检查返回的数据中是否包含用户信息的关键字段
            if "userId" in data and "status" in data:
                # status为2表示正常状态
                return data.get("status") == 2
        return False
    except (requests.RequestException, json.JSONDecodeError) as e:
        return False

def get_valid_cookie(save_user_info: bool = True) -> tuple[Optional[str], Optional[Dict[Any, Any]]]:
    """
    从环境变量文件获取有效的cookie并可选保存用户信息

    Args:
        save_user_info (bool): 是否保存用户信息到user.json

    Returns:
        tuple[Optional[str], Optional[Dict]]: 返回(cookie, user_info)，如果无效则返回(None, None)
    """
    # 从环境变量文件读取cookie列表
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    cookies = []
    
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('YUANBAO_COOKIE='):
                        cookie = line.strip().split('=', 1)[1].strip('"\'')
                        cookies.append(cookie)
    except Exception as e:
        print(f"读取环境变量文件失败: {e}")
        return None, None

    # 测试每个cookie直到找到有效的
    for cookie in cookies:
        test_url = "https://yuanbao.tencent.com/api/getuserinfo"
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                if user_info.get("status") == 2:
                    if save_user_info:
                        # 保存用户信息到user.json
                        with open(os.path.join(os.path.dirname(__file__), 'user.json'), 'w', encoding='utf-8') as f:
                            json.dump(user_info, f, ensure_ascii=False, indent=4)
                    return cookie, user_info
        except Exception as e:
            logger.error(f"测试cookie失败: {cookie}, 错误: {e}")
            continue
    
    return None, None
