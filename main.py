from yuanbao_chat import chat_with_yuanbao
from utils.cookie_manager import get_valid_cookie

if __name__ == "__main__":
    # 获取有效的cookie
    cookie, user_info = get_valid_cookie() # 获取有效的cookie和用户信息
    if not cookie:
        print("没有可用的cookie，请检查.env文件")
        exit(1)
    
    uuid = "f4bdc441-e09e-4a9a-9e9f-1fa97c17d91b"  # 替换为您的会话UUID
    message = "你都会什么？"  # 替换为您要发送的消息

    # 调用函数与腾讯元宝API交互
    print("正在与回答中...")
    merged_thoughts, merged_output = chat_with_yuanbao(cookie, uuid, message, model="v3")

    # 打印合并后的思考和输出内容
    print("思考内容:\n", merged_thoughts, "\n")
    print("回答内容:\n", merged_output)