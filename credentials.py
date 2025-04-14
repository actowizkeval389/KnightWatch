import pymysql
def get_db_connection():
    return pymysql.connect(
        host="15.235.85.189",
        user="root",
        password="actowiz",
        database="knightwatch",
        cursorclass=pymysql.cursors.DictCursor
    )