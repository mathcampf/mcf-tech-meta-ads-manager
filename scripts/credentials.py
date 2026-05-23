import os
import json
import pathlib

def get_credentials():
    """
    Busca credenciais em cascata:
    1. Variáveis de ambiente (Claude Code CLI com settings.json)
    2. Arquivo ~/.mcf-tech/meta-ads-config.json (Cowork, Windows, Mac, Linux)
    """
    token = os.environ.get("META_ACCESS_TOKEN")
    account_id = os.environ.get("META_AD_ACCOUNT_ID")

    if token and account_id:
        return token, account_id

    config_path = pathlib.Path.home() / ".mcf-tech" / "meta-ads-config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            token = cfg.get("META_ACCESS_TOKEN")
            account_id = cfg.get("META_AD_ACCOUNT_ID")
        except Exception:
            pass

    return token, account_id


def require_credentials():
    """Retorna credenciais ou encerra o script com mensagem de erro."""
    token, account_id = get_credentials()
    if not token or not account_id:
        print("ERRO: Credenciais não encontradas.")
        print("")
        print("Execute o skill 'setup' para configurar suas credenciais.")
        print("O arquivo de configuração deve estar em:")
        print(f"  {pathlib.Path.home() / '.mcf-tech' / 'meta-ads-config.json'}")
        exit(1)
    return token, account_id
