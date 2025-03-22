import aiohttp
import asyncio
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramSender:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def async_send_message(self, chat_id, text):
        """Асинхронная функция отправки сообщения в Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info(f"✅ Успешно отправлено в Telegram ID {chat_id}")
                        return True
                    else:
                        logger.error(f"❌ Ошибка Telegram API: {result}")
                        return False
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в Telegram: {e}")
            return False

    def sync_send_message(self, chat_id, text):
        """Синхронная обёртка для асинхронной отправки"""
        try:
            return asyncio.run(self.async_send_message(chat_id, text))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.async_send_message(chat_id, text))


# Создаём экземпляр класса
telegram_sender = TelegramSender(settings.TELEGRAM_BOT_TOKEN)
