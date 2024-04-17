# Description: This file contains the DatabaseManager class, which is responsible for managing the database.
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from Tables import Base
from lib.SessionManager import SessionManager



class DatabaseManager:    
    def __init__(self, database_uri="sqlite:///users.db"):
        self.engine = create_engine(database_uri, echo=True)
        self.metadata = MetaData()
        self.session_maker = sessionmaker(bind=self.engine)
        self.create_tables()
        
        self.SM = SessionManager()
        self.SM.set_session_maker(self.session_maker)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        
        
    @property
    def create_user(self):
        @self.SM.session_management(auto_commit=True)
        def _create_user(username, password, session: Session=None): # add parameters here
            from Tables import User
            user = User(username=username, password=password)
            session.add(user)
        return _create_user
    
    @property
    def authenticate_user(self):
        @self.SM.session_management(auto_commit=False)
        def _authenticate_user(username, password, session: Session=None):
            from Tables import User
            user = session.query(User).filter(User.username == username).first()
            if user is None:
                return False
            return user.password == password
        return _authenticate_user
        
    
        
        
    
    
    

    
        
        
        
    

    