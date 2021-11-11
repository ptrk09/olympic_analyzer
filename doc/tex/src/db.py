import psycopg2 as pg
from datetime import datetime

class AbstractDataBase:
    def __init__(self, dbname=None, user=None, password=None, host=None) -> None:
        check = dbname is None or user is None or password is None or host is None
        if check: raise ValueError()
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__host = host
        self.conn = None
        self.cursor = None


    def connect(self, dbname=None, user=None, password=None, host=None):
        self.conn = pg.connect(
            dbname=self.__dbname if dbname is None else dbname, 
            user=self.__user if user is None else user, 
            password=self.__password if password is None else password, 
            host=self.__host if host is None else host 
        )
        self.cursor = self.conn.cursor()


    def close(self):
        self.cursor.close()
        self.conn.close()


class OlympicDataBase(AbstractDataBase):
    def __init__(self, dbname=None, user=None, password=None, host=None) -> None:
        super().__init__(dbname=dbname, user=user, password=password, host=host)

    def get_commets(self):
        list_data = list()
        self.cursor.execute(
            'select comments.id, auth_user.username, comments.content, ' + 
		    'comments.date_comment, comments.time_comment ' +
            'from comments ' +
            'join auth_user on auth_user.id = comments.id_user ' +
            'order by comments.date_comment desc, comments.time_comment desc;'
        )

        for row in self.cursor:
            list_data.append({
                'id' : row[0],
                "username" : row[1],
                "content" : row[2],
                "date" : row[3],
                "time" : row[4]
            })
        
        return list_data

    def append_comment(self, user_name, text):
        date = datetime.now()
        day = "-".join(list(map(str, [date.day, date.month, date.year]))) 
        time = ":".join(list(map(str, [date.hour, date.minute, date.second])))
        print(day, time)

        self.cursor.execute(
            "select auth_user.id " +
            "from auth_user " +
            "where auth_user.username = %s;", (str(user_name),) 
        )

        print(self.cursor.query)
        
        user_id = self.cursor.fetchall()[0][0]
        
        self.cursor.execute(
            "INSERT INTO comments (id_user, content) " +
            "VALUES (%s, %s);", (str(user_id), str(text))
        )
        self.conn.commit()
    

    def delete_comment(self, id_comment):
        self.cursor.execute(
            "DELETE FROM comments " +
            "where id= %s;", (str(id_comment))
        )
        self.conn.commit()


    def users_info(self):
        list_data = list()

        self.cursor.execute(
            "SELECT id, last_login, username, email, " + 
            "is_staff, is_active, date_joined " +
            "from auth_user " +
            "where is_superuser is false;"
        )

        for row in self.cursor:
            list_data.append({
                'id' : row[0],
                "last_login" : row[1],
                "username" : row[2],
                "email" : row[3],
                "is_staf" : row[4],
                "is_active" : row[5],
                "date_joined" : row[6]
            })
        
        return list_data

    
    def delete_user(self, id):
        self.cursor.execute(
            "DELETE FROM auth_user " +
            "where id= %s;", (str(id))
        )
        self.conn.commit()
