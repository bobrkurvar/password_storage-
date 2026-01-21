class User:
    def __init__(self):
        pass

class Roles:
    def __init__(self, name: str):
        self.name = name

class UserRoles:
    def __init__(self, user_id: int, role_name: str):
        self.user_id = user_id
        self.role_name = role_name

# class Admins:
#     def __init__(self, user_id: int):
#         self.id = user_id