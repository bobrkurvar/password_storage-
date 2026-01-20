import logging

log = logging.getLogger(__name__)

async def check_access_and_refresh_token(access_token: str | None, refresh_token: str | None, ext_api_manager, state):
    has_refresh_or_access = True

    if not access_token:
        log.info("access token не существует")
        access_time = 900
        if refresh_token:
            log.info("refresh token существует")
            refresh_time = 86400 * 7
            tokens = await ext_api_manager.refresh(refresh_token)
            await state.storage.set_token(
                state.key,
                token_name="access_token",
                token_value=tokens.get("access_token"),
                ttl=access_time,
            )
            await state.storage.set_token(
                state.key,
                token_name="refresh_token",
                token_value=tokens.get("refresh_token"),
                ttl=refresh_time,
            )
        else:
            has_refresh_or_access = False
    else:
        log.info("access token существует")

    return has_refresh_or_access
