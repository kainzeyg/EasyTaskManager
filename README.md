# EasyTaskManager

## 🚀 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/kainzeyg/EasyTaskManager.git
   cd EasyTaskManager
   ```

2. Запустите сборку и запуск контейнеров:
   ```bash
   docker-compose up -d --build
   ```

## 🐳 Контейнеры

Проект поднимается в виде нескольких Docker-контейнеров:

- **`backend`** — Python API
- **`db`** — MySQL база данных  
  💡 Объем постоянного хранилища можно увеличить, изменив последний блок в `docker-compose.yml`
- **`interface`** — TypeScript интерфейс  
  🔧 Требует Node.js версии > 18
- **`nginx`** — веб-сервер  
  📁 Конфигурация: `interface/nginx.conf`
- **`redis`** — необходим для хранения сессий
