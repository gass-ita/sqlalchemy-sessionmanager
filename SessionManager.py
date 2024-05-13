from functools import wraps
from typing import Union
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.orm.session import _SessionBind
import logging
import time
from contextlib import contextmanager




class SessionManager:
    def __init__(self, engine: _SessionBind):
        self.engine = engine
        self.session_maker = sessionmaker(bind=engine)

    def __init__(self, session_maker: sessionmaker):
        self.engine = None
        self.session_maker = session_maker

    def __init__(self):
        self.session_maker = None

    def set_engine(self, engine: _SessionBind):
        self.engine = engine
        self.session_maker = sessionmaker(bind=engine)

    def set_session_maker(self, session_maker: sessionmaker):
        self.engine = None
        self.session_maker = session_maker
        
    @contextmanager
    def session_manager(self, auto_commit: bool=False, reload_after_commit: bool=None, verbose: Union[int, bool]=logging.ERROR):
        """
        Context manager to manage the session for the database operations.

        If a session is provided as a parameter, it will be used. Otherwise, a new session will be created and closed after the function is called.

        args:
            auto_commit (bool): If True, the session will be committed after the function is called and all the attributes of the session. Defaults to False.
            reload_after_commit (bool): If True, all the objects in the session will be reloaded after the commit. Defaults to auto_commit. If auto_commit is False, this parameter is ignored.
            verbose (Union[int, bool]): If True, the logging level will be set to logging.INFO. If False, the logging level will be set to logging.ERROR. If an int, the logging level will be set to that value. Defaults to logging.ERROR.


        This context manager is used to manage the session for the database operations.
        
        This function can be used as a context manager to manage the session for the database operations.
        
        For example:
        
        with session_manager(auto_commit=True) as session:
            # perform database operations using the session
            ...
        """
        
        if not reload_after_commit:
            reload_after_commit = auto_commit

        # Set up logging
        if isinstance(verbose, bool):
            verbose = logging.INFO if verbose else logging.ERROR

        logging.basicConfig(level=verbose)

        if not self.session_maker:
            raise ValueError("session_maker is not set.")
        else:
            logging.info("session_maker is set.")

        logging.info("session management called...")
        
        session: Union[Session | None] = self.session_maker()
        logging.info("session created...")

        try:
            yield session
        except:
            logging.info("rolling back session...")
            session.rollback()
            session.close()
        finally:
            self.__cleanup_session__(session, auto_commit, reload_after_commit, verbose)


    def session_management(self, auto_commit: bool=False, reload_after_commit: bool=None, verbose: Union[int, bool]=logging.ERROR):
        """
        Decorator to manage the session for the database operations.

        If a session is provided as a parameter, it will be used. Otherwise, a new session will be created and closed after the function is called.

        args:
            auto_commit (bool): If True, the session will be committed after the function is called and all the attributes of the session. Defaults to False.
            reload_after_commit (bool): If True, all the objects in the session will be reloaded after the commit. Defaults to auto_commit. If auto_commit is False, this parameter is ignored.
            verbose (Union[int, bool]): If True, the logging level will be set to logging.INFO. If False, the logging level will be set to logging.ERROR. If an int, the logging level will be set to that value. Defaults to logging.ERROR.


        This decorator is used to manage the session for the database operations.

        Add to the parameters of the function to be decorated a parameter called session with a default value of None.

        The function will be called with the session as a parameter, and the session will be closed after the function is called.

        If the function raises an exception, the session will be rolled back and closed.
        """
        
        if not reload_after_commit:
            reload_after_commit = auto_commit

        # Set up logging
        if isinstance(verbose, bool):
            verbose = logging.INFO if verbose else logging.ERROR

        logging.basicConfig(level=verbose)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.session_maker:
                    raise ValueError("session_maker is not set.")
                else:
                    logging.info("session_maker is set.")

                logging.info("session management called...")
                
                if "session" in kwargs and kwargs["session"]:
                    logging.info("session provided...")
                    return func(*args, **kwargs)

                logging.info("session not provided, creating one...")
                session: Union[Session | None] = self.session_maker()
                logging.info("session created...")

                try:
                    kwargs["session"] = session
                    result = func(*args, **kwargs)
                    return result
                except:
                    logging.info("rolling back session...")
                    session.rollback()
                    session.close()
                finally:
                    self.__cleanup_session__(session, auto_commit, reload_after_commit, verbose)
                        
                        

            return wrapper

        return decorator
    
    @staticmethod
    def __cleanup_session__(session: Session, auto_commit: bool=False, reload_after_commit: bool=None, verbose: Union[int, bool]=logging.ERROR):
        """
        Cleans up the session after the function is called.
        """
        
        logging.basicConfig(level=verbose)
        
        if not session or not session.is_active:
            logging.warning("session is None or inactive!")
            return
            
        if auto_commit:
            try:
                logging.info("committing session...")
                try:
                    session.commit()
                except IntegrityError:
                    logging.info("rolling back session...")
                    session.rollback()
                    session.close()
                    
                logging.info("committed!")
                # reload all the objects
                if reload_after_commit:
                    logging.info("reloading objects...")
                    start_time = time.time()
                    for obj in session:
                        session.refresh(obj)
                    end_time = time.time()
                    logging.info("reloaded in %d ms!", (end_time - start_time) * 1000)
            except InvalidRequestError:
                pass
        else:
            if reload_after_commit:
                logging.warning("reload_after_commit is set to True, but auto_commit is set to False. Ignoring reload_after_commit.")
        
        
        if session.is_active:
            try:
                logging.info("closing session...")
                session.close()
                logging.info("closed!")
                pass
                
            except InvalidRequestError:
                logging.info("already closed!")
                pass
