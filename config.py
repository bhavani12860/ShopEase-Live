import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "shopease-secret-key"
    )

    MYSQL_HOST = os.environ.get(
        "DB_HOST",
        "localhost"
    )

    MYSQL_PORT = int(os.environ.get(
        "DB_PORT",
        "3306"
    ))

    MYSQL_USER = os.environ.get(
        "DB_USER",
        "root"
    )

    MYSQL_PASSWORD = os.environ.get(
        "DB_PASSWORD",
        ""
    )

    MYSQL_DATABASE = os.environ.get(
        "DB_NAME",
        "shopease_db"
    )