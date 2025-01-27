from bs4 import BeautifulSoup
import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        # 移除HTML标签
        text = BeautifulSoup(text, "html.parser").get_text()
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        # 移除特殊字符
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text 