from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import dotenv_values

env = dotenv_values("config.env")

db_username = env["DB_USERNAME"]
db_pwd = env["DB_PASSWORD"]
db_name = env["DB_NAME"]
db_host = env["DB_HOST"]

# Create an engine to connect to the database
DbEngine = create_engine(
    f'postgresql+psycopg2://{db_username}:{db_pwd}@{db_host}/{db_name}',
    echo=True)

# Create a base class for all models
ModelsBase = declarative_base()

# Create a session maker
DbSession = sessionmaker(bind=DbEngine)

from src.models.user import User
from src.models.enrolled_task import EnrolledTask
from src.models.transaction import Transaction
from src.models.task import Task
from src.models.state_data import StateData
