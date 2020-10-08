import sqlite3

class UserData:
    def __init__(self):
        print("Loading database by sqlite3")
        self.connect = sqlite3.connect('database.db', check_same_thread=False)
        print("Load database successfully")
        self.cursor = self.connect.cursor()
        self.cursor.execute('''CREATE TABLE if not exists USERLIST
            (USERNAME TEXT PRIMARY KEY NOT NULL,
            EMAIL TEXT NOT NULL,
            PASSWORD TEXT NOT NULL);''')
        print("Loaded table successfully")
        self.connect.commit()

    def create_new_user(self,username,email,password):
        try :
            self.cursor.execute(f"INSERT INTO USERLIST VALUES ('{username}', '{email}', '{password}')")
            self.connect.commit()
        except :
            return False
        return True

    def find_username(self,username):
        print(f"to find {username}")
        data = self.cursor.execute(f"SELECT USERNAME, EMAIL, PASSWORD from USERLIST where USERNAME='{username}'")
        for item in data:
            item = list(item)
            return item

    def print(self):
        data = self.cursor.execute("SELECT USERNAME, EMAIL, PASSWORD from USERLIST")
        return data


def main():
    print("Start test")
    db = UserData()
    db.create_new_user("kaidouo","hikper@gmail.com","what")
    db.print()
    db.find_username("kaidouo")
    db.find_username("noexixt")

if __name__=="__main__":
    main()