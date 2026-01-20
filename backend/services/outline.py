import logging
import os
import re
import base64
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from backend.utils.text_client import get_text_chat_client

logger = logging.getLogger(__name__)


class OutlineService:
    def __init__(self):
        logger.debug("初始化 OutlineService...")
        self.text_config = self._load_text_config()
        self.client = self._get_client()
        self.prompt_template = self._load_prompt_template()
        logger.info(f"OutlineService 初始化完成，使用服务商: {self.text_config.get('active_provider')}")

    def _load_text_config(self) -> dict:
        """加载文本生成配置"""
        config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'
        logger.debug(f"加载文本配置: {config_path}")

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                logger.debug(f"文本配置加载成功: active={config.get('active_provider')}")
                return config
            except yaml.YAMLError as e:
                logger.error(f"文本配置 YAML 解析失败: {e}")
                raise ValueError(
                    f"文本配置文件格式错误: text_providers.yaml\n"
                    f"YAML 解析错误: {e}\n"
                    "解决方案：检查 YAML 缩进和语法"
                )

        logger.warning("text_providers.yaml 不存在，使用默认配置")
        # 默认配置
        return {
            'active_provider': 'google_gemini',
            'providers': {
                'google_gemini': {
                    'type': 'google_gemini',
                    'model': 'gemini-2.0-flash-exp',
                    'temperature': 1.0,
                    'max_output_tokens': 8000
                }
            }
        }

    def _get_client(self):
        """根据配置获取客户端"""
        active_provider = self.text_config.get('active_provider', 'google_gemini')
        providers = self.text_config.get('providers', {})

        if not providers:
            logger.error("未找到任何文本生成服务商配置")
            raise ValueError(
                "未找到任何文本生成服务商配置。\n"
                "解决方案：\n"
                "1. 在系统设置页面添加文本生成服务商\n"
                "2. 或手动编辑 text_providers.yaml 文件"
            )

        if active_provider not in providers:
            available = ', '.join(providers.keys())
            logger.error(f"文本服务商 [{active_provider}] 不存在，可用: {available}")
            raise ValueError(
                f"未找到文本生成服务商配置: {active_provider}\n"
                f"可用的服务商: {available}\n"
                "解决方案：在系统设置中选择一个可用的服务商"
            )

        provider_config = providers.get(active_provider, {})

        if not provider_config.get('api_key'):
            logger.error(f"文本服务商 [{active_provider}] 未配置 API Key")
            raise ValueError(
                f"文本服务商 {active_provider} 未配置 API Key\n"
                "解决方案：在系统设置页面编辑该服务商，填写 API Key"
            )

        logger.info(f"使用文本服务商: {active_provider} (type={provider_config.get('type')})")
        return get_text_chat_client(provider_config)

    def _load_prompt_template(self, mode: str = "outline", style: str = "sketch") -> str:
        if mode == "poster":
            filename = "poster_prompt.txt"
        else:
            # 根据风格选择大纲提示词
            filename = "outline_prompt_classic.txt" if style == "classic" else "outline_prompt_sketch.txt"
            
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            filename
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _parse_outline(self, outline_text: str) -> List[Dict[str, Any]]:
        # 按 <page> 分割页面（兼容旧的 --- 分隔符）
        if '<page>' in outline_text:
            pages_raw = re.split(r'<page>', outline_text, flags=re.IGNORECASE)
        else:
            # 向后兼容：如果没有 <page> 则使用 ---
            pages_raw = outline_text.split("---")

        pages = []

        for index, page_text in enumerate(pages_raw):
            page_text = page_text.strip()
            if not page_text:
                continue

            page_type = "content"
            type_match = re.match(r"\[(\S+)\]", page_text)
            if type_match:
                type_cn = type_match.group(1)
                type_mapping = {
                    "封面": "cover",
                    "内容": "content",
                    "总结": "summary",
                }
                page_type = type_mapping.get(type_cn, "content")

            pages.append({
                "index": index,
                "type": page_type,
                "content": page_text
            })

        return pages

    def generate_outline(
        self,
        topic: str,
        images: Optional[List[bytes]] = None,
        mode: str = "outline",
        style: str = "sketch"
    ) -> Dict[str, Any]:
        """
        生成大纲或海报内容
        
        Args:
            topic: 主题
            images: 图片列表 (bytes)
            mode: 模式 "outline" 或 "poster"
            style: 风格 "sketch" (手绘) 或 "classic" (经典)
            
        Returns:
            Dict matching OutlineResponse schema
        """
        try:
            # 防御性检查：确保 images 是列表类型
            if images is not None and not isinstance(images, list):
                logger.warning(f"images 参数类型错误: {type(images)}, 将设为 None")
                images = None
            
            image_count = len(images) if images else 0
            logger.info(f"开始生成大纲: topic={topic[:50]}..., mode={mode}, style={style}, images={image_count}")
            
            # 1. 准备提示词
            prompt = self._load_prompt_template(mode, style).format(topic=topic)
            if images and image_count > 0:
                prompt += f"\n\n注意：用户提供了 {image_count} 张参考图片，请在生成大纲时考虑这些图片的内容和风格。"
                logger.debug(f"添加了 {image_count} 张参考图片到提示词")

            # 2. 获取配置和客户端
            active_provider = self.text_config.get('active_provider', 'google_gemini')
            providers = self.text_config.get('providers', {})
            provider_config = providers.get(active_provider, {})
            model = provider_config.get('model', 'gemini-2.0-flash-exp')
            
            # 3. 调用 API
            logger.info(f"调用文本生成 API: model={model}")
            raw_text = self.client.generate_text(
                prompt=prompt,
                model=model,
                temperature=provider_config.get('temperature', 1.0),
                max_output_tokens=provider_config.get('max_output_tokens', 8000),
                images=images
            )
            
            logger.debug(f"API 返回文本长度: {len(raw_text)} 字符")

            # 4. 处理返回结果
            from backend.schemas import OutlineResponse, PosterData
            
            if mode == "poster":
                return self._process_poster_response(raw_text, mode, images)
            else:
                return self._process_outline_response(raw_text, mode, images)

        except Exception as e:
            logger.exception("大纲生成服务发生未处理异常")
            # 返回标准的错误结构
            return {
                "success": False,
                "mode": mode,
                "error": str(e),
                "has_images": False
            }

    def _process_poster_response(self, text: str, mode: str, images: Optional[List[bytes]]) -> Dict[str, Any]:
        """处理海报模式响应"""
        import json
        from backend.schemas import PosterData
        
        try:
            # 使用正则提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', text.strip())
            if not json_match:
                raise ValueError("LLM 未返回有效的 JSON 结构")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # 使用 Pydantic 验证
            poster_data = PosterData(**data)
            
            return {
                "success": True,
                "mode": mode,
                "poster_data": poster_data.model_dump(),
                "outline": text, # 保留原始文本用于调试
                "has_images": bool(images)
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"海报数据解析失败: {e}\nRaw Text: {text[:200]}...")
            return {
                "success": False,
                "mode": mode,
                "error": f"生成内容格式错误: {str(e)}",
                "outline": text
            }
        except Exception as e:
            logger.exception("海报处理未知错误")
            return {
                "success": False,
                "mode": mode,
                "error": f"处理出错: {str(e)}",
                "outline": text
            }

    def _process_outline_response(self, text: str, mode: str, images: Optional[List[bytes]]) -> Dict[str, Any]:
        """处理普通大纲响应"""
        pages = self._parse_outline(text)
        return {
            "success": True,
            "mode": mode,
            "outline": text,
            "pages": pages,
            "has_images": bool(images)
        }

def get_outline_service() -> OutlineService:
    """
    获取大纲生成服务实例
    每次调用都创建新实例以确保配置是最新的
    """
    return OutlineService()
