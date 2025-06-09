from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import settings


class SingletonDatabaseConnection:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()  # Initialize database connection
        return cls._instance

    def init_db(self):
        # Initialize the connection
        self.SQLALCHEMY_DATABASE_URL = settings.db_url
        self.engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                bind=self.engine,
            )
        )
        self.Base = declarative_base()

    def get_session(self):
        return self.session


# Instantiate Singleton
db_instance = SingletonDatabaseConnection()

# Export Base and get_session for external use
Base = db_instance.Base
