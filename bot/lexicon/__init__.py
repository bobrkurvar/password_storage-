from pydantic import BaseModel
from .core_lexicon import COMMAND_CORE

class Phrases(BaseModel):
    start: str = COMMAND_CORE['start']
    help: str = COMMAND_CORE['help']

phrases = Phrases()