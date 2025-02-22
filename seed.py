from database import session
from models import User, Word, UserWord

# Системный пользователь для общих слов
SYSTEM_USER_ID = 0

# Список начальных слов (английский - русский)
INITIAL_WORDS = [
    ("hello", "привет"),
    ("world", "мир"),
    ("apple", "яблоко"),
    ("cat", "кот"),
    ("dog", "собака"),
    ("house", "дом"),
    ("book", "книга"),
    ("water", "вода"),
    ("tree", "дерево"),
    ("car", "машина"),
    ("sun", "солнце"),
    ("moon", "луна"),
    ("computer", "компьютер"),
    ("phone", "телефон"),
    ("table", "стол"),
    ("chair", "стул"),
    ("pen", "ручка"),
    ("paper", "бумага"),
    ("food", "еда"),
    ("friend", "друг"),
    ("school", "школа"),
    ("work", "работа"),
    ("time", "время"),
    ("day", "день"),
    ("night", "ночь"),
    ("week", "неделя"),
    ("month", "месяц"),
    ("year", "год"),
    ("city", "город"),
    ("country", "страна"),
    ("language", "язык"),
    ("music", "музыка"),
    ("film", "фильм"),
    ("road", "дорога"),
    ("money", "деньги"),
    ("love", "любовь"),
    ("family", "семья"),
    ("child", "ребенок"),
    ("man", "мужчина"),
    ("woman", "женщина"),
    ("sky", "небо"),
    ("earth", "земля"),
    ("fire", "огонь"),
    ("water", "вода"),
    ("flower", "цветок"),
    ("animal", "животное"),
    ("bird", "птица"),
    ("fish", "рыба"),
    ("happy", "счастливый"),
    ("sad", "грустный")
]


def seed_initial_words():
    # Создаем системного пользователя если его нет
    system_user = session.query(User).filter_by(telegram_id=SYSTEM_USER_ID).first()
    if not system_user:
        system_user = User(telegram_id=SYSTEM_USER_ID, username="system")
        session.add(system_user)
        session.commit()

    # Добавляем слова
    for en, ru in INITIAL_WORDS:
        if not session.query(Word).filter_by(english=en).first():
            word = Word(english=en, russian=ru, created_by=system_user.id)
            session.add(word)

    session.commit()

    # Связываем слова со всеми пользователями
    all_users = session.query(User).filter(User.telegram_id != SYSTEM_USER_ID).all()
    system_words = session.query(Word).filter_by(created_by=system_user.id).all()

    for user in all_users:
        for word in system_words:
            if not session.query(UserWord).filter_by(user_id=user.id, word_id=word.id).first():
                user_word = UserWord(user_id=user.id, word_id=word.id)
                session.add(user_word)

    session.commit()


if __name__ == "__main__":
    seed_initial_words()
    print("База данных заполнена начальными словами!")