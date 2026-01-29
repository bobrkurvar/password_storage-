class User:
    def __init__(self):
        pass


class Role:
    def __init__(self, name: str):
        self.name = name


class UserRole:
    def __init__(self, user_id: int, role_name: str):
        self.user_id = user_id
        self.role_name = role_name


class Admin:
    def __init__(self, user_id: int):
        self.id = user_id
