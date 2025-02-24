from sqlalchemy import func
from database import session
from models import User, Word, UserWord

SYSTEM_USER_ID = 0

# Список начальных слов
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
    ("flower", "цветок"),
    ("animal", "животное"),
    ("bird", "птица"),
    ("fish", "рыба"),
    ("happy", "счастливый"),
    ("sad", "грустный"),
]

def add_initial_words():
    """Добавление начальных слов в таблицу слов"""
    for en, ru in INITIAL_WORDS:
        if not session.query(Word).filter_by(english=en).first():
            word = Word(english=en, russian=ru)
            session.add(word)
    session.commit()

def get_user(user_id):
    """Получение пользователя по его Telegram ID"""
    return session.query(User).filter_by(telegram_id=user_id).first()

def add_user(user_id, username):
    """Добавление нового пользователя в базу данных"""
    user = User(telegram_id=user_id, username=username)
    session.add(user)
    session.commit()
    return user

def seed_initial_words(user_id):
    """Связывание пользователя с 4 случайными словами"""
    user = get_user(user_id)
    if not user:
        user = add_user(user_id, "default_username")

    # Получаем 4 случайных слова, которые еще не изучены пользователем
    words = session.query(Word).join(UserWord, isouter=True).filter(
        (UserWord.user_id == user.id) | (UserWord.user_id == None)
    ).order_by(func.random()).limit(4).all()

    # Добавление пользователя к этим словам
    for word in words:
        if not session.query(UserWord).filter_by(user_id=user.id, word_id=word.id).first():
            user_word = UserWord(user_id=user.id, word_id=word.id)
            session.add(user_word)
    session.commit()

def delete_user_word(user_id, word_id):
    """Удаление слова у пользователя"""
    deleted = session.execute(
        """
        DELETE FROM user_words 
        WHERE user_id = :user_id AND word_id = :word_id
        RETURNING id
        """,
        {'user_id': user_id, 'word_id': word_id}
    ).fetchone()

    if deleted:
        session.commit()
        return True
    return False