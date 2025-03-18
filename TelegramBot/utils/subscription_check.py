from config import REQUIRED_CHANNEL_ID, REQUIRED_GROUP_ID


async def check_subscription(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на необходимые каналы и группы"""
    from aiogram import Bot

    bot = Bot.get_current()

    try:
        # Проверяем подписку на канал
        channel_member = await bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        channel_status = channel_member.status

        # Проверяем подписку на группу
        group_member = await bot.get_chat_member(REQUIRED_GROUP_ID, user_id)
        group_status = group_member.status

        # Пользователь должен быть участником обоих
        valid_statuses = ["member", "administrator", "creator"]
        return channel_status in valid_statuses and group_status in valid_statuses

    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False
