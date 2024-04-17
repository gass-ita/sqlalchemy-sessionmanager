from DatabaseManager import DatabaseManager

db1 = DatabaseManager(database_uri="sqlite:///users.db")
db2 = DatabaseManager(database_uri="sqlite:///users2.db")

db1.create_user(username="user1", password="user1")
db2.create_user(username="user2", password="user2")