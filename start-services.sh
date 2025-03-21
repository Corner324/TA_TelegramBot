#!/bin/bash

docker network inspect shop_shared_network >/dev/null 2>&1 || docker network create shop_shared_network

# Запускаем бэкенд
docker-compose -f ./Server/docker-compose.yml up -d

# Чтобы БД успела запуститься
sleep 10

# Запускаем бота
docker-compose -f ./TelegramBot/docker-compose.yml up -d

echo "Все сервисы запущены" 