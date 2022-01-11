import sqlite3
from sqlite3 import Error
import wsb_post


class Database:
    def __init__(self):
        # open/create the db
        db = None
        self.dbPath = "wsb_ml.db"
        try:
            db = sqlite3.connect(self.dbPath)

            # make some tables for the db if they don't exist yet
            self.query("CREATE TABLE IF NOT EXISTS PostLearningData "
                       "(postId varchar(1000),"
                       "ticker varchar(10), "
                       "postTitle varchar(1000), "
                       "postDescription varchar(10000), "
                       "tenMinuteWinner INT,"
                       "thirtyMinuteWinner INT,"
                       "oneHourWinner INT,"
                       "postTime INT);")

            # print initialization
            print("Db initialized at", self.dbPath, "on version", sqlite3.version)
        except Error as e:
            print("Error:", e)
        finally:
            if db:
                db.close()

    def query(self, query):
        try:
            db = sqlite3.connect(self.dbPath)
            db.execute(query)
            db.commit()
            db.close()
        except Error as e:
            print("Error:", e)
        finally:
            if db:
                db.close()

    def connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.dbPath)
        except Error as e:
            print("Error:", e)

        return conn

    def get_all_post_records(self):
        conn = self.connection()

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM PostLearningData;")

        rows = cursor.fetchall()

        postList = []
        for row in rows:
            p = wsb_post.WSBPost()
            p.postId =                      row[0]
            p.ticker =                      row[1]
            p.title =                       row[2]
            p.description =                 row[3]
            p.tenMinuteWinner =             bool(row[4])
            p.thirtyMinuteWinner =          bool(row[5])
            p.oneHourWinner =               bool(row[6])
            p.postTime =                    int(row[7])
            postList.append(p)

        return postList

    def add_post_record(self, postRecord: wsb_post.WSBPost):
        # make the articleRecord table query
        self.query("INSERT INTO PostLearningData VALUES ('" +
                   str(postRecord.postId) + "', '" +
                   str(postRecord.ticker) + "', '" +
                   str(postRecord.title) + "', '" +
                   str(postRecord.description) + "', '" +
                   str(1 if postRecord.tenMinuteWinner else 0) + "', '" +
                   str(1 if postRecord.thirtyMinuteWinner else 0) + "', '" +
                   str(1 if postRecord.oneHourWinner else 0) + "', '" +
                   str(postRecord.postTime) + "');")