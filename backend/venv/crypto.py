import hashlib

def hash_password(password, salt):
    m_password = password
    m_salt = salt
    dataBase_password = m_password + m_salt
    hashed = hashlib.md5(dataBase_password.encode())
    return hashed.hexdigest()

def hash_file_name(password):
    m_password = password
    hashed = hashlib.md5(m_password.encode())
    return hashed.hexdigest()
