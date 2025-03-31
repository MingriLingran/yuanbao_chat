# token_counter.py
"""
AI模型Token计算模块（类型安全版）
功能特性：
1. 完全类型标注，通过mypy/pyright严格校验
2. 支持离线模式和本地配置文件校验
3. 自动处理所有异常，不支持的模型返回0
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union

# 配置离线模式环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # type: ignore
os.environ["HF_DATASETS_OFFLINE"] = "1"   # type: ignore

# 配置日志系统
logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger("TokenCounter")

try:
    from transformers import AutoTokenizer
    from transformers.tokenization_utils import PreTrainedTokenizer
    from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
except ImportError as e:
    logger.error("缺少必要依赖库：transformers")
    raise RuntimeError("必须安装transformers库") from e

# 定义类型别名
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

class TokenCalculator:
    """
    Token计算核心类
    
    属性：
    - tokenizers: 字典类型，保存已加载的tokenizer实例
    - SUPPORTED_MODELS: 支持的模型与目录映射
    
    方法：
    - calculate_tokens: 计算指定模型的token数量
    - available_models: 获取可用模型列表的属性
    """
    
    SUPPORTED_MODELS = {
        "deepseekr1": "deepseek-r1-tokenizer",
        "deepseekv3": "deepseek-v3-tokenizer",
        # "hunyuant1": "hunyuan-t1-tokenizer"
    }

    def __init__(self, tokenizer_dir: str = "utils/tokenizers") -> None:
        """
        初始化Token计算器
        
        参数：
        tokenizer_dir -- tokenizer配置文件的根目录，默认为"tokenizers"
        
        异常：
        FileNotFoundError -- 当配置文件缺失时抛出
        """
        self.tokenizer_dir = Path(tokenizer_dir)
        self._validate_directory()  # 启动时目录校验
        
        # 初始化tokenizers字典 {模型名: tokenizer实例}
        self.tokenizers: Dict[str, Optional[TokenizerType]] = {
            model: self._load_tokenizer(dir_name)
            for model, dir_name in self.SUPPORTED_MODELS.items()
        }

    def _validate_directory(self) -> None:
        """验证配置文件目录结构和必要文件"""
        if not self.tokenizer_dir.exists():
            raise FileNotFoundError(f"Token目录不存在：{self.tokenizer_dir}")
            
        # 各模型需要的核心配置文件
        required_files = {
            "deepseek-r1-tokenizer": ["tokenizer.json", "tokenizer_config.json"],
            "deepseek-v3-tokenizer": ["tokenizer.json", "tokenizer_config.json"],
            # "hunyuan-t1-tokenizer": ["tokenizer.model", "tokenizer_config.json"]
        }
        
        for dir_name, files in required_files.items():
            dir_path = self.tokenizer_dir / dir_name
            # 目录检查
            if not dir_path.is_dir():
                raise NotADirectoryError(f"配置目录错误：{dir_path}")
                
            # 文件存在性检查
            missing = [f for f in files if not (dir_path / f).is_file()]
            if missing:
                raise FileNotFoundError(
                    f"{dir_name} 缺少文件：{', '.join(missing)}\n"
                    f"解决方案：\n"
                    f"1. 从模型官网下载配置文件\n"
                    f"2. 放置到 {dir_path} 目录"
                )

    def _load_tokenizer(self, dir_name: str) -> Optional[TokenizerType]:
        """
        安全加载tokenizer实例
        
        参数：
        dir_name -- tokenizer配置目录名称
        
        返回：
        Tokenizer实例或None（加载失败时）
        """
        dir_path = self.tokenizer_dir / dir_name
        
        try:
            # 注意：AutoTokenizer.from_pretrained返回Union类型
            return AutoTokenizer.from_pretrained(  # type: ignore[return-value]
                str(dir_path),
                trust_remote_code=True,  # 必须允许远程代码执行
                local_files_only=True,   # 强制离线模式
                use_fast=False           # 确保兼容性
            )
        except Exception as e:
            logger.warning(
                f"加载tokenizer失败：{dir_name}\n"
                f"错误类型：{type(e).__name__}\n"
                f"详细信息：{str(e)}"
            )
            return None

    def calculate_tokens(self, model_name: str, text: str) -> int:
        """
        计算指定模型的token数量
        
        参数：
        model_name -- 模型名称（不区分大小写）
        text -- 需要计算token的文本
        
        返回：
        token数量（遇到错误时返回0）
        """
        model_name = model_name.lower()
        
        # 检查模型是否支持
        if model_name not in self.SUPPORTED_MODELS:
            logger.debug(f"不支持的模型：{model_name}")
            return 0
            
        # 获取tokenizer实例
        tokenizer = self.tokenizers[model_name]
        if tokenizer is None:
            logger.debug(f"tokenizer未正确加载：{model_name}")
            return 0
            
        try:
            # 特殊模型的编码规则
            if model_name == "deepseekv3":
                encoded = tokenizer.encode(text, add_special_tokens=False)
            else:
                encoded = tokenizer.encode(text)
            return len(encoded)
        except Exception as e:
            logger.debug(
                f"编码失败：{model_name}\n"
                f"错误类型：{type(e).__name__}\n"
                f"输入文本：{text[:50]}...\n"
                f"详细信息：{str(e)}"
            )
            return 0

    @property
    def available_models(self) -> list[str]:
        """获取当前可用模型列表（成功加载tokenizer的模型）"""
        return [m for m, t in self.tokenizers.items() if t is not None]

# 示例用法
if __name__ == "__main__":
    try:
        # 初始化计算器
        calculator = TokenCalculator()
        print(f"支持的模型：{calculator.available_models}")
        
        # 测试用例
        test_cases = [
            ("DeepSeekR1", "大语言模型Token计算原理"),  # 正确模型
            ("invalid_model", "无效模型测试"),        # 不支持的模型
            ("deepseekv3", "Attention is all you need"),  # 正确模型
            ("hunyuant1", "测试空字符串"),  # 正常文本
            ("hunyuant1", "")  # 空文本测试
        ]
        
        for model, text in test_cases:
            count = calculator.calculate_tokens(model, text)
            status = "✓" if count > 0 else "✗"
            print(f"[{status}] {model}: '{text[:15]}...' → Tokens: {count}")
            
    except FileNotFoundError as e:
        print(f"配置文件错误：{str(e)}")
    except Exception as e:
        print(f"未知错误：{type(e).__name__} - {str(e)}")