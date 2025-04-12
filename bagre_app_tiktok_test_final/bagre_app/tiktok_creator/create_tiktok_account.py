
import json
from .utils import gerar_email_temporario

def criar_conta_tiktok():
    email = gerar_email_temporario()
    usuario = f"user_{email.split('@')[0]}"
    senha = "SenhaForte123"

    conta = {
        "email": email,
        "usuario": usuario,
        "senha": senha
    }

    with open("bagre_app/data/tiktok_contas.json", "a") as f:
        f.write(json.dumps(conta) + "\n")

    return {"status": "sucesso", "conta": conta}
