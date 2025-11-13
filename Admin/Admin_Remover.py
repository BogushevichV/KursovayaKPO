from DataBase.Base_User_Remover import BaseUserRemover

class AdminRemover:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.base_remover = BaseUserRemover("admins", dbname, user, password, host, port)
    
    def remove_admin(self, login: str) -> bool:
        return self.base_remover.remove_account(login)