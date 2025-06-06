from passlib.hash import bcrypt

def get_hash_from_pas(pas: str):
    pas_hash = bcrypt.hash(pas)
    return pas_hash


