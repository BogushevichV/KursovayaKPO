from DataBase.Base_User_Creator import BaseUserCreator

class UserCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.base_creator = BaseUserCreator("users", dbname, user, password, host, port)
    
    def create_user(self, login: str, password: str, email: str, **extra_fields) -> bool:
        return self.base_creator.create_account(login, password, email, **extra_fields)