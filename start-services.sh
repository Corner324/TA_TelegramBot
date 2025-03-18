#!/bin/bash

docker network inspect shop_shared_network >/dev/null 2>&1 || docker network create shop_shared_network

# Запускаем бэкенд
docker-compose -f docker-compose.backend.yml up -d

# Чтобы БД успела запуститься
sleep 10

# Запускаем бота
docker-compose -f docker-compose.bot.yml up -d

echo "Все сервисы запущены" 