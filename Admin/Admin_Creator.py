from DataBase.Base_User_Creator import BaseUserCreator

class AdminCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.base_creator = BaseUserCreator("admins", dbname, user, password, host, port)
    
    def create_admin(self, login: str, password: str, email: str, **extra_fields) -> bool:
        return self.base_creator.create_account(login, password, email, **extra_fields)