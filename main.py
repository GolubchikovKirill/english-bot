import telebot
from telebot import types
import random
from models import User, Word, UserWord
from database import session, init_db
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
user_states = {}

# Главное меню
def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎓 Изучать английский", "📝 Добавить слово", "ℹ️ Помощь", "🗑️ Удалить слово")
    return markup

# Обработчик старта
@bot.message_handler(commands=["start"])
def start(message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        session.add(user)
        session.commit()

        # Добавляем системные слова новому пользователю
        system_user = session.query(User).filter_by(telegram_id=0).first()
        if system_user:
            system_words = session.query(Word).all()  # Убираем фильтрацию по created_by
            for word in system_words:
                user_word = UserWord(user_id=user.id, word_id=word.id)
                session.add(user_word)
            session.commit()

    bot.send_message(
        message.chat.id,
        "Привет! Давай учить английский!",
        reply_markup=main_markup()
    )

# Помощь
@bot.message_handler(func=lambda m: m.text == "ℹ️ Помощь")
def help(message):
    text = (
        "📚 Это бот для изучения английских слов.\n\n"
        "🎓 Нажми 'Изучать английский' для начала тренировки\n"
        "📝 Используй 'Добавить слово' для добавления новых слов\n"
        "🗑️ Удаляй ненужные слова с помощью 'Удалить слово'\n"
        "ℹ️ Здесь ты можешь получить справку о функциях бота"
    )
    bot.send_message(message.chat.id, text)

# Добавление слова
@bot.message_handler(func=lambda m: m.text == "📝 Добавить слово")
def add_word(message):
    msg = bot.send_message(message.chat.id, "Введи слово на английском:")
    bot.register_next_step_handler(msg, process_english)

def process_english(message):
    user_states[message.from_user.id] = {"english": message.text}
    msg = bot.send_message(message.chat.id, "Теперь введи перевод на русском:")
    bot.register_next_step_handler(msg, process_russian)

def process_russian(message):
    user_id = message.from_user.id
    english = user_states[user_id]["english"]
    russian = message.text

    user = session.query(User).filter_by(telegram_id=user_id).first()

    # Создаем новое слово
    new_word = Word(english=english, russian=russian)
    session.add(new_word)
    session.commit()

    # Связываем с пользователем
    user_word = UserWord(user_id=user.id, word_id=new_word.id)
    session.add(user_word)
    session.commit()

    del user_states[user_id]
    bot.send_message(message.chat.id, "✅ Слово успешно добавлено!", reply_markup=main_markup())

# Удаление слова
@bot.message_handler(func=lambda m: m.text == "🗑️ Удалить слово")
def delete_word(message):
    msg = bot.send_message(message.chat.id, "Введите слово, которое хотите удалить:")
    bot.register_next_step_handler(msg, process_word_to_delete)

def process_word_to_delete(message):
    user_id = message.from_user.id
    word_to_delete = message.text

    user = session.query(User).filter_by(telegram_id=user_id).first()

    word = session.query(Word).filter_by(english=word_to_delete).first()
    if word:
        user_word = session.query(UserWord).filter_by(user_id=user.id, word_id=word.id).first()
        if user_word:
            session.delete(user_word)
            session.commit()
            bot.send_message(message.chat.id, f"Слово '{word_to_delete}' удалено!", reply_markup=main_markup())
        else:
            bot.send_message(message.chat.id, f"Слово '{word_to_delete}' не найдено у вас!", reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"Слово '{word_to_delete}' не найдено в базе данных.",
                         reply_markup=main_markup())

# Обучение
@bot.message_handler(func=lambda m: m.text == "🎓 Изучать английский")
def study(message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    words = (
        session.query(Word)
        .join(UserWord)
        .filter(UserWord.user_id == user.id, UserWord.learned == False)
        .limit(4)  # Получаем только 4 случайных слова
        .all()
    )

    if not words:
        bot.send_message(message.chat.id, "Ты пока не добавил ни одного слова 😢")
        return

    word = random.choice(words)
    correct = word.russian

    # Генерация неправильных ответов
    all_ru = [w.russian for w in session.query(Word).filter(Word.russian != correct).all()]
    wrong = random.sample(all_ru, 4) if len(all_ru) >= 4 else ["Ошибка загрузки"] * 4

    options = [correct] + wrong
    random.shuffle(options)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        markup.add(types.KeyboardButton(opt))

    user_states[message.from_user.id] = {
        "word_id": word.id,
        "correct": correct,
        "attempts": 0
    }

    bot.send_message(
        message.chat.id,
        f"Как перевести слово: **{word.english}**?",
        parse_mode="Markdown",
        reply_markup=markup
    )

# Проверка ответа
@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def check_answer(message):
    user_id = message.from_user.id
    data = user_states[user_id]

    if message.text == data["correct"]:
        # Обновляем статистику
        user_word = (
            session.query(UserWord)
            .filter_by(
                user_id=session.query(User.id).filter_by(telegram_id=user_id).scalar(),
                word_id=data["word_id"]
            )
            .first()
        )
        user_word.correct_attempts += 1

        if user_word.correct_attempts >= 3:
            user_word.learned = True
            session.commit()
            bot.send_message(message.chat.id, "🎉 Слово выучено!", reply_markup=main_markup())
        else:
            session.commit()
            bot.send_message(message.chat.id, "✅ Правильно! Еще разок?", reply_markup=main_markup())

        del user_states[user_id]
    else:
        data["attempts"] += 1
        if data["attempts"] >= 2:
            bot.send_message(
                message.chat.id,
                f"❌ Неверно. Правильный ответ: {data['correct']}",
                reply_markup=main_markup()
            )
            del user_states[user_id]
        else:
            bot.send_message(message.chat.id, "😕 Попробуй еще раз:")

if __name__ == "__main__":
    print('bot is running')
    init_db()
    bot.infinity_polling()