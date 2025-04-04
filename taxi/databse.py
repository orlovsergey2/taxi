from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import text
from typing import Optional

class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, nullable=False)
    release_year: int = Field(nullable=False)
    genre: str = Field(max_length=50, nullable=False)
    collection_in_mil: float = Field(nullable=False)

def create_connection_url(host, port, user, password, database=None):
    if database:
        return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}"

def main():
    host = "127.0.0.1"
    port = "9306"
    user = "myuser"
    password = "mypassword"
    database = "movie"

    # 1. Создание БД (если не существует)
    url = create_connection_url(host, port, user, password)
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))
        print(f"База данных {database} создана или уже существует")

    # 2. Подключение к БД
    url_with_db = create_connection_url(host, port, user, password, database)
    engine_with_db = create_engine(url_with_db)

    # 3. Создание таблиц
    SQLModel.metadata.create_all(engine_with_db)
    print("Таблица movies создана или уже существует")

    # 4. Вставка данных
    movies_data = [
        Movie(title="Forrest Gump", release_year=1994, genre="Drama", collection_in_mil=330.2),
        Movie(title="3 Idiots", release_year=2009, genre="Drama", collection_in_mil=2.4),
        Movie(title="Eternal Sunshine of the Spotless Mind", release_year=2004, genre="Drama", collection_in_mil=34.5),
        Movie(title="Good Will Hunting", release_year=1997, genre="Drama", collection_in_mil=138.1),
        Movie(title="Skyfall", release_year=2012, genre="Action", collection_in_mil=304.6),
        Movie(title="Gladiator", release_year=2000, genre="Action", collection_in_mil=188.7),
        Movie(title="Black", release_year=2005, genre="Drama", collection_in_mil=3.0),
        Movie(title="Titanic", release_year=1997, genre="Romance", collection_in_mil=659.2),
        Movie(title="The Shawshank Redemption", release_year=1994, genre="Drama", collection_in_mil=28.4),
        Movie(title="Udaan", release_year=2010, genre="Drama", collection_in_mil=1.5),
        Movie(title="Home Alone", release_year=1990, genre="Comedy", collection_in_mil=286.9),
        Movie(title="Casablanca", release_year=1942, genre="Romance", collection_in_mil=1.0)
    ]

    with Session(engine_with_db) as session:
        session.add_all(movies_data)
        session.commit()
        print(f"Добавлено {len(movies_data)} фильмов")

if __name__ == '__main__':
    main()
