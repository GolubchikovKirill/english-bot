# seed.py
from database import session
from models import User, Word, UserWord

SYSTEM_USER_ID = 0

# Список начальных слов
INITIAL_WORDS = [
    ("hello", "привет"),
    ("world", "мир"),
    # Добавьте остальные слова...
]

def add_initial_words():
    # Добавление начальных слов в таблицу слов
    for en, ru in INITIAL_WORDS:
        if not session.query(Word).filter_by(english=en).first():
            word = Word(english=en, russian=ru)
            session.add(word)
    session.commit()

def get_user(user_id):
    return session.query(User).filter_by(telegram_id=user_id).first()

def add_user(user_id, username):
    user = User(telegram_id=user_id, username=username)
    session.add(user)
    session.commit()
    return user

def seed_initial_words(user_id):
    # Получаем пользователя, или создаем его, если его нет
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

if __name__ == "__main__":
    add_initial_words()
    print("База данных заполнена начальными словами!")