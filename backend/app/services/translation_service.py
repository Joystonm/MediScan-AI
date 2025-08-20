import logging
from typing import List

logger = logging.getLogger(__name__)

class TranslationService:
    """Simplified translation service for development."""
    
    def __init__(self):
        logger.info("Translation service initialized (mock mode)")
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Mock translation - returns original text."""
        return text
    
    async def translate_list(self, text_list: List[str], target_language: str) -> List[str]:
        """Mock translation for lists - returns original list."""
        return text_list
