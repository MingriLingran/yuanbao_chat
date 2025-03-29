# Yuanbao Chat

一个用于与腾讯元宝AI助手进行对话的Python工具。

## 功能?

- [x] 自动管理和验证cookie信息
- [x] 支持不同版本的AI模型选择  
- [ ] 支持openai兼容
- [ ] 网络调用
  
## 环境要求

- Python 3.6+
- 需要有效的腾讯元宝账号cookie

## 安装方法

1. 克隆项目到本地
2. 在项目根目录创建.env文件，配置cookie信息

```Properties
YUANBAO_COOKIE="cookie1_here"
YUANBAO_COOKIE="cookie2_here"
YUANBAO_COOKIE="cookie3_here"
```

## 使用方法

1. 确保.env文件中包含有效的cookie配置
2. 修改main.py文件中的message
3. 运行代码：

```PowerShell
PS: python main.py
```

## 注意事项

- 请妥善保管您的cookie信息
- 建议定期更新cookie以确保正常使用

## 示例输出

```plaintext
思考内容:
[AI的思考过程]

回答内容:
[AI的回答内容]
```
