# bagre_app_preview (5 apps)

Prévia mínima funcional para testes locais. Inclui:
- 5 instâncias Flask (bagre, bagre2, bagre3, bagre4, bagre5)
- Login por usuário/senha
- Painel com vídeos reais (TikTok e YouTube Shorts) embutidos
- Botões de "Curtir" e "Comentar" que registram interações localmente (SQLite)
- Detector de "tempo assistido" (posta evento após 3s assistidos)

## Requisitos
- Python 3.10+
- pip

## Instalação (uma vez só)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r common_requirements.txt
```

## Rodando os 5 apps
```bash
chmod +x run_all.sh
./run_all.sh
```
Acesse no navegador:
- http://localhost:5001 (bagre / 91980514xx)
- http://localhost:5002 (bagre2 / 91980514xx)
- http://localhost:5003 (bagre3 / 91980514xx)
- http://localhost:5004 (bagre4 / 91980514xx)
- http://localhost:5005 (bagre5 / 91980514xx)

## Proxies
Em cada pasta, edite o arquivo `.env` e configure:
```env
PROXY_HTTP=http://usuario:senha@host:porta
PROXY_HTTPS=http://usuario:senha@host:porta
```
As interações locais são registradas no SQLite (`data/app.db`). O proxy é deixado pronto para futuras chamadas HTTP reais.

## Limitações desta prévia
- Os botões de curtir/comentar **não** acionam as plataformas externas (restrição de CORS/automação). Eles registram o evento localmente para validação de fluxo.
- Uso em modo desenvolvimento (Flask). Para produção, usar gunicorn + reverse proxy.

## Estrutura
- `app_*/app.py`: servidor Flask de cada instância
- `templates/`: páginas HTML (login, painel)
- `static/app.js`: lógica de interação/telemetria
- `data/app.db`: banco SQLite com eventos
- `common_requirements.txt`: dependências comuns
- `run_all.sh`: sobe as 5 instâncias

## Resetar banco
Delete a pasta `data/` de cada app (será recriada no próximo start).
```
