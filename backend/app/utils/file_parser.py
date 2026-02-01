"""
文件解析工具
支持PDF、Markdown、TXT文件的文本提取
支持扫描版 PDF 的 OCR 识别
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileParser:
    """文件解析器"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt'}
    
    # OCR 相关配置
    OCR_ENABLED = True  # 是否启用 OCR
    OCR_LANG = 'chi_sim+eng'  # OCR 语言：简体中文 + 英文
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        从文件中提取文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {suffix}")
        
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.md', '.markdown'}:
            return cls._extract_from_md(file_path)
        elif suffix == '.txt':
            return cls._extract_from_txt(file_path)
        
        raise ValueError(f"无法处理的文件格式: {suffix}")
    
    @classmethod
    def _extract_from_pdf(cls, file_path: str) -> str:
        """从PDF提取文本，支持扫描版 PDF 的 OCR"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("需要安装PyMuPDF: pip install PyMuPDF")
        
        text_parts = []
        ocr_used = False
        
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                # 首先尝试直接提取文本
                text = page.get_text()
                
                if text.strip():
                    text_parts.append(text)
                elif cls.OCR_ENABLED:
                    # 如果页面没有文本，尝试使用 OCR
                    ocr_text = cls._ocr_page(page, page_num + 1)
                    if ocr_text.strip():
                        text_parts.append(ocr_text)
                        ocr_used = True
        
        if ocr_used:
            logger.info(f"PDF 使用了 OCR 识别: {file_path}")
        
        return "\n\n".join(text_parts)
    
    @classmethod
    def _ocr_page(cls, page, page_num: int) -> str:
        """使用 OCR 识别 PDF 页面"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # 配置 Tesseract 路径
            # 1. 优先从环境变量读取（推荐在 .env 中配置 TESSERACT_CMD）
            tesseract_cmd = os.environ.get('TESSERACT_CMD')
            if tesseract_cmd and os.path.exists(tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            else:
                # 2. 回退到跨平台默认路径
                default_paths = [
                    # Windows - 常见安装路径
                    r"E:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"D:\Program Files\Tesseract-OCR\tesseract.exe",
                    # Linux
                    "/usr/bin/tesseract",
                    "/usr/local/bin/tesseract",
                    # macOS (Homebrew)
                    "/opt/homebrew/bin/tesseract",
                    "/usr/local/Cellar/tesseract/*/bin/tesseract",
                ]
                for path in default_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
                    
        except ImportError:
            logger.warning(f"第 {page_num} 页无文本且 OCR 依赖未安装，跳过")
            return ""
        
        try:
            import fitz
            
            # 将页面渲染为图片（使用 2x 缩放提高清晰度）
            zoom = 2.0  # 缩放倍数
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # 转换为 PIL Image
            image = Image.open(io.BytesIO(img_data))
            
            # 使用 Tesseract OCR
            text = pytesseract.image_to_string(image, lang=cls.OCR_LANG)
            
            logger.debug(f"OCR 第 {page_num} 页: 提取 {len(text)} 字符")
            return text
            
        except pytesseract.TesseractNotFoundError:
            logger.warning(f"Tesseract OCR 未安装，无法识别第 {page_num} 页")
            return ""
        except Exception as e:
            logger.warning(f"OCR 第 {page_num} 页失败: {e}")
            return ""
    
    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        """从Markdown提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """从TXT提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @classmethod
    def extract_from_multiple(cls, file_paths: List[str]) -> str:
        """
        从多个文件提取文本并合并
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            合并后的文本
        """
        all_texts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                text = cls.extract_text(file_path)
                filename = Path(file_path).name
                all_texts.append(f"=== 文档 {i}: {filename} ===\n{text}")
            except Exception as e:
                all_texts.append(f"=== 文档 {i}: {file_path} (提取失败: {str(e)}) ===")
        
        return "\n\n".join(all_texts)


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[str]:
    """
    将文本分割成小块
    
    Args:
        text: 原始文本
        chunk_size: 每块的字符数
        overlap: 重叠字符数
        
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            # 查找最近的句子结束符
            for sep in ['。', '！', '？', '.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 下一个块从重叠位置开始
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

