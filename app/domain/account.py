class Account:
    def __init__(self, account_id: int, user_id: int, password: str, name: str):
        self.account_id = account_id
        self.user_id = user_id
        self.password = password
        self.name = name


class Param:
    def __init__(
        self,
        param_id: int,
        account_id: int,
        name: str,
        content: str,
        secret: bool = False,
    ):
        self.param_id = param_id
        self.account_id = account_id
        self.name = name
        self.content = content
        self.secret = secret
