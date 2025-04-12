
import random
import string

def gerar_email_temporario():
    nome = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{nome}@exemplo.com"
