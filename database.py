from flask import g
import sqlite3

# connect db to app
def connect_db():
    sql = sqlite3.connect("./db/questions.db")
    sql.row_factory = sqlite3.Row   # replace tuples with dicts
    return sql

# get connected db
def get_db():
    if not hasattr(g, "sqlite3"):
        g.sqlite_db = connect_db()
    return g.sqlite_db