from DatabaseManager import DatabaseManager

db1 = DatabaseManager(database_uri="sqlite:///users.db")
db2 = DatabaseManager(database_uri="sqlite:///users2.db")

db1.create_user(username="user1", password="user1")
db2.create_user(username="user2", password="user2")

with db1.SM.session_manager(auto_commit=True) as session:
    from Tables import User
    session.add(User(username="user3", password="user3"))
    
with db1.SM.session_manager(auto_commit=True, raise_error_types=(ZeroDivisionError)) as session:
    from Tables import User
    session.add(User(username="user4", password="user4"))
    x = 5/0

print("Users in db1:")
    
    
