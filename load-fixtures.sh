#!/bin/bash

echo "🚀 Загружаем тестовые данные в контейнер Django..."

docker exec -it backend_api python manage.py loaddata catalog/fixtures/catalog_data.json
docker exec -it backend_api python manage.py loaddata faq/fixtures/faq_data.json

echo "✅ Данные успешно загружены!"
