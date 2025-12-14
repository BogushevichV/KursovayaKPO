from Client.Back.client_requests import DatabaseServerClient


class AccountManager:
    """Универсальный менеджер для создания и удаления аккаунтов пользователей и администраторов"""
    
    def __init__(self, server_url: str = "http://localhost:5000", **kwargs):
        """Инициализация менеджера аккаунтов"""
        self.client = DatabaseServerClient(server_url)
    
    def create_account(self, account_type: str, login: str, password: str, email: str, **extra_fields) -> bool:
        """Создание аккаунта (пользователя или администратора)"""
        if account_type not in ['user', 'admin']:
            raise ValueError(f"Неизвестный тип аккаунта: {account_type}. Используйте 'user' или 'admin'")
        
        try:
            if account_type == 'user':
                result = self.client.create_user(login, password, email, **extra_fields)
            else:  # admin
                result = self.client.create_admin(login, password, email, **extra_fields)
            
            if result:
                print(f"Аккаунт '{login}' успешно создан в таблице {account_type}s")
            else:
                print(f"Ошибка: не удалось создать аккаунт '{login}' в таблице {account_type}s")
            
            return result
        except Exception as e:
            print(f"Ошибка при создании аккаунта '{login}' в таблице {account_type}s: {e}")
            return False
    
    def delete_account(self, account_type: str, login: str) -> bool:
        """Удаление аккаунта (пользователя или администратора)"""
        if account_type not in ['user', 'admin']:
            raise ValueError(f"Неизвестный тип аккаунта: {account_type}. Используйте 'user' или 'admin'")
        
        try:
            if account_type == 'user':
                result = self.client.remove_user(login)
            else:  # admin
                result = self.client.remove_admin(login)
            
            if result:
                print(f"Аккаунт '{login}' успешно удалён из таблицы {account_type}s")
            else:
                print(f"Аккаунт с логином '{login}' не найден в таблице {account_type}s")
            
            return result
        except Exception as e:
            print(f"Ошибка при удалении аккаунта '{login}' из таблицы {account_type}s: {e}")
            return False

