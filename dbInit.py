import sqlite3


conn = sqlite3.connect('UCID.db')
cursor = conn.cursor()
cursor.execute("""CREATE TABLE ids
                  (chat_id INTEGER NOT NULL UNIQUE)
""")
conn.close()