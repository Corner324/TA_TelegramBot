from config import REQUIRED_CHANNEL_ID, REQUIRED_GROUP_ID
from aiogram import Bot, Router

import logging


router = Router()
logger = logging.getLogger(__name__)

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на необходимые каналы и группы"""
    try:
        # Проверяем подписку на канал
        channel_member = await bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        channel_status = channel_member.status
       
        # Проверяем подписку на группу
        group_member = await bot.get_chat_member(REQUIRED_GROUP_ID, user_id)
        group_status = group_member.status

        # Пользователь должен быть участником обоих
        valid_statuses = ["member", "administrator", "creator"]
        is_valid = channel_status in valid_statuses and group_status in valid_statuses
        logger.info(f"Результат проверки подписки: {is_valid}, user_id: {user_id}")
        return is_valid

    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}, user_id: {user_id}")
        return False