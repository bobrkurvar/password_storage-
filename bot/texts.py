from pydantic import BaseModel

COMMAND_CORE = {
    "start": "<b>БОТ ДЛЯ ХРАНЕНИЯ ПАРОЛЕЙ\nДля Регистрации: REGISTER\nДля Списка рессурсов: RESOURCES\nДля создания рессурса: CREATE RESOURCE</b>",
    "help": "<b>Как работать с ботом:</b>\n\n<b>1)</b> Пройдите регистрацию или авторизуйтесь\n<b>2)</b> Откройте нужный рессурс из списка ресурсов(RESOURCES) или создайте новый(CREATE RESOURCE)"
    "\n<b>3)</b> В открытом русурсе создайте аккаунт(для этого нужно будет ввести его логин и пароль которые вы хотите сохранить в данном боте-хранилище)"
    "или откройте интересующий вас аккаунт и посмотрите свой пароль",
}

AUTHENTICATION = {
    "login": "<b>Для входа введите пароль</b>",
    "register": "<b>Для регистрации введите пароль</b>",
    "already_registered": "<b>Пользователь уже зарегистрирован</b>",
    "user_not_exists": "<b>Пользователь не зарегистрирован</b>",
    "need unlock": "Введите master password для разблокировки хранилища",
    "wrong password": "Неверный пароль, введите заново",
}

ACCOUNT = {
    "account name": "<b>Введите имя аккаунта</b>",
    "account password": "<b>Введите пароль от аккаунта</b>",
    "account created": "<b>Аккаунт {} создан</b>",
    "account_param": "<b>{}: {}\n </b>",
    "account params": "<b>Введите через пробел параметры для аккаунта в виде:\n"
    "параметр_1 параметр_2 ... параметр_n\nили нажмите menu если дополнительные параметры не нужны</b>",
    "empty accounts list": "список аккаунтов пуст"
}


class Phrases(BaseModel):
    start: str = COMMAND_CORE["start"]
    help: str = COMMAND_CORE["help"]
    need_register: str = AUTHENTICATION["register"]
    login: str = AUTHENTICATION["login"]
    already_reg: str = AUTHENTICATION["already_registered"]
    user_not_exists: str = AUTHENTICATION["user_not_exists"]
    account_params: str = ACCOUNT["account params"]
    account_name: str = ACCOUNT["account name"]
    account_password: str = ACCOUNT["account password"]
    account_created: str = ACCOUNT["account created"]
    account_param: str = ACCOUNT["account_param"]
    need_unlock: str = AUTHENTICATION["need unlock"]
    wrong_password: str = AUTHENTICATION["wrong password"]
    empty_accounts_list: str = ACCOUNT["empty accounts list"]


phrases: Phrases = Phrases()
