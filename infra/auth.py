import hmac
from core import conf


def get_user_id_with_compare_key(
    user_id: int,
    api_key: str
) -> int:
    is_valid = hmac.compare_digest(
        api_key,
        conf.internal_api_key,
    )
    if not is_valid:
        raise ValueError("Не верный ключ")

    return user_id