from os import getenv
from cryptography.fernet import Fernet


encryption_key = getenv("ENCRYPTION_KEY")


def encrypt(text):
    fernet_encrypter = Fernet(encryption_key)

    encoded_encrypted_text = fernet_encrypter.encrypt(bytes(text, "utf-8"))
    encrypted_text = encoded_encrypted_text.decode("utf-8")

    return encrypted_text


def decrypt(encrypted_text):
    fernet_encrypter = Fernet(encryption_key)

    encoded_decrypted_text = fernet_encrypter.decrypt(encrypted_text)
    decrypted_text = encoded_decrypted_text.decode("utf-8")

    return decrypted_text
