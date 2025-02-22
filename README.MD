# English Learning Bot

Телеграм-бот для изучения английских слов с персональной базой данных.

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/GolubchikovKirill/english-bot.git
cd english-bot


# Документация English Learning Bot

## Функционал
- Персональный словарь для каждого пользователя
- Система повторения слов с интервалами
- Добавление пользовательских слов
- Статистика изучения
- База начальных слов (50 основных слов)

## Структура БД
### Таблицы
1. `users` - данные пользователей
   - id (PK)
   - telegram_id (UNIQUE)
   - username

2. `words` - словарная база
   - id (PK)
   - english (UNIQUE)
   - russian
   - created_by (FK to users.id)

3. `user_words` - связь пользователей со словами
   - id (PK)
   - user_id (FK to users.id)
   - word_id (FK to words.id)
   - learned (BOOL)
   - attempts (INT)
   - correct_attempts (INT)

## Архитектура
- `bot.py` - основной файл с логикой бота
- `database.py` - инициализация БД
- `models.py` - модели SQLAlchemy
- `seed.py` - наполнение начальными данными
- 'config' - токены(файл нужно создать самостоятельно)
TOKEN - токен бота
DATABASE_URL - url для подключения к бд