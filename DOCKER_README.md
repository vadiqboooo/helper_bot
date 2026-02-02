# Запуск бота в Docker

## Установка Docker на Linux

### Ubuntu / Debian

```bash
# Обновляем пакеты
sudo apt update

# Устанавливаем необходимые зависимости
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавляем официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновляем список пакетов
sudo apt update

# Устанавливаем Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Проверяем установку
sudo docker --version

# Добавляем пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Перезагружаемся или выполняем команду для применения изменений
newgrp docker

# Включаем автозапуск Docker
sudo systemctl enable docker
sudo systemctl start docker
```


## Быстрый старт

### 1. Убедитесь, что Docker установлен
```bash
docker --version
docker compose version
```

### 2. Убедитесь, что файл .env заполнен
Проверьте, что в файле `.env` указаны все необходимые переменные:
- `BOT_TOKEN` - токен от @BotFather
- `ADMIN_ID` - ваш Telegram ID
- `OPENROUTER_API_KEY` - API ключ OpenRouter

### 3. Запустите бота
```bash
# Собрать и запустить контейнер
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Остановить бота
docker-compose down

# Перезапустить бота
docker-compose restart
```

## Полезные команды

### Просмотр логов
```bash
# Все логи
docker-compose logs

# Последние 100 строк
docker-compose logs --tail=100

# В реальном времени
docker-compose logs -f
```

### Перезапуск после изменений кода
```bash
# Пересобрать образ и перезапустить
docker-compose up -d --build
```

### Остановка и удаление контейнера
```bash
docker-compose down
```

### Очистка (удаление образов)
```bash
# Удалить контейнер и образ
docker-compose down --rmi all
```

## Структура файлов

- `Dockerfile` - инструкции для создания Docker образа
- `docker-compose.yml` - конфигурация для запуска контейнера
- `.dockerignore` - файлы, которые не попадут в образ
- `.env` - переменные окружения (НЕ коммитить в Git!)
- `.env.example` - пример файла с переменными окружения

## База данных

База данных `homework_bot.db` автоматически сохраняется на хосте, поэтому при перезапуске контейнера все данные сохраняются.

## Автоматический перезапуск

Контейнер настроен на автоматический перезапуск (`restart: unless-stopped`), поэтому бот будет автоматически запускаться при перезагрузке сервера.

## Мониторинг

Проверить статус контейнера:
```bash
docker-compose ps
```

Проверить использование ресурсов:
```bash
docker stats helper_bot
```

## Развертывание на сервере

### Копирование проекта на сервер

```bash
# С помощью git
git clone https://your-repo-url.git
cd helper_bot_2.0

# Или копирование файлов через scp
scp -r /path/to/helper_bot_2.0 user@server:/path/to/destination/
```

### Настройка .env файла на сервере

```bash
# Создайте .env файл
nano .env

# Добавьте переменные окружения:
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
OPENROUTER_API_KEY=your_api_key

# Сохраните (Ctrl+O, Enter, Ctrl+X)
```

### Запуск в фоновом режиме

```bash
# Запуск
docker compose up -d

# Проверка логов
docker compose logs -f

# Остановка по Ctrl+C, бот продолжит работать в фоне
```

## Распространенные проблемы

### Permission denied при запуске docker

**Проблема:** `Got permission denied while trying to connect to the Docker daemon socket`

**Решение:**
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Перезайдите в систему или выполните
newgrp docker

# Или используйте sudo
sudo docker compose up -d
```

### Порт уже занят

**Проблема:** Контейнер не запускается из-за занятого порта

**Решение:**
```bash
# Проверьте запущенные контейнеры
docker ps -a

# Остановите старый контейнер
docker stop helper_bot
docker rm helper_bot

# Перезапустите
docker compose up -d
```

### База данных не сохраняется

**Проблема:** После перезапуска контейнера данные теряются

**Решение:** Убедитесь, что в `docker-compose.yml` указан volume:
```yaml
volumes:
  - ./homework_bot.db:/app/homework_bot.db
```

### Ошибка "No such file or directory"

**Проблема:** Docker не может найти .env файл

**Решение:**
```bash
# Убедитесь, что .env файл существует в корне проекта
ls -la .env

# Если его нет, создайте из примера
cp .env.example .env
nano .env
```

### Контейнер постоянно перезапускается

**Проблема:** Бот падает сразу после запуска

**Решение:**
```bash
# Смотрим логи для выяснения причины
docker compose logs

# Проверяем, что все переменные окружения заполнены
cat .env

# Проверяем правильность BOT_TOKEN
```

## Обновление бота

### Обновление кода

```bash
# Остановите контейнер
docker compose down

# Обновите код (через git или копирование файлов)
git pull

# Пересоберите образ и запустите
docker compose up -d --build

# Проверьте логи
docker compose logs -f
```

### Обновление зависимостей

Если изменился `requirements.txt`:
```bash
# Пересоберите образ
docker compose build --no-cache

# Перезапустите контейнер
docker compose up -d
```

## Безопасность

### Защита .env файла

```bash
# Установите правильные права доступа
chmod 600 .env

# Убедитесь, что .env в .gitignore
cat .gitignore | grep .env
```

### Настройка файрвола (опционально)

Если нужно ограничить доступ к серверу:
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## Автозапуск при загрузке сервера

Docker уже настроен на автозапуск (`restart: unless-stopped`), но убедитесь, что служба Docker запускается при загрузке:

```bash
sudo systemctl enable docker
sudo systemctl status docker
```
