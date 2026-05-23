# Skill: meta-setup
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Configura as credenciais de acesso à API do Meta Ads. Cria o arquivo de configuração no caminho padrão do sistema, compatível com Windows, Mac e Linux. Funciona tanto no Claude Code CLI quanto no Cowork.

---

## Instruções para o Claude

Siga exatamente esta sequência. Responda sempre em português. Aguarde confirmação do usuário antes de avançar entre os passos.

---

## Passo 1 — Verificar configuração existente

Execute o script abaixo para checar se já existe configuração:

```bash
python3 -c "
import pathlib, json
p = pathlib.Path.home() / '.mcf-tech' / 'meta-ads-config.json'
if p.exists():
    cfg = json.loads(p.read_text())
    t = cfg.get('META_ACCESS_TOKEN','')
    a = cfg.get('META_AD_ACCOUNT_ID','')
    print('ENCONTRADO')
    print(f'Token: {t[:15]}...' if t else 'Token: NAO DEFINIDO')
    print(f'Account ID: {a}' if a else 'Account ID: NAO DEFINIDO')
else:
    print('NAO ENCONTRADO')
    print(f'Caminho esperado: {p}')
"
```

- Se retornar `ENCONTRADO` com valores preenchidos, vá direto ao Passo 4.
- Se não existir ou estiver incompleto, continue para o Passo 2.

---

## Passo 2 — Obter o Token de Acesso

Explique ao usuário:

> **Como gerar seu token:**
> 1. Acesse [developers.facebook.com](https://developers.facebook.com)
> 2. Menu superior → **Ferramentas** → **Explorador da Graph API**
> 3. Selecione o app no canto superior direito
> 4. Clique em **Gerar token de acesso**
> 5. Marque as permissões: `ads_read`, `ads_management`, `business_management`
> 6. Copie o token (começa com `EAA...`)
>
> ⚠️ Não compartilhe este token. Trate-o como senha.

Peça ao usuário que cole o token aqui na conversa quando estiver pronto.

---

## Passo 3 — Obter o ID da Conta de Anúncios

Explique ao usuário:

> **Como encontrar seu ID:**
> 1. Acesse [business.facebook.com](https://business.facebook.com) → Gerenciador de Anúncios
> 2. Olhe a URL: você verá `act_XXXXXXXXX`
> 3. Esse número com o prefixo `act_` é o seu ID

Peça ao usuário que informe o ID da conta.

---

## Passo 4 — Salvar as credenciais

Com o token e o account ID em mãos, execute (substituindo os valores reais):

```bash
python3 -c "
import pathlib, json
config_dir = pathlib.Path.home() / '.mcf-tech'
config_dir.mkdir(parents=True, exist_ok=True)
config_path = config_dir / 'meta-ads-config.json'
config_path.write_text(json.dumps({
    'META_ACCESS_TOKEN': 'TOKEN_AQUI',
    'META_AD_ACCOUNT_ID': 'ACCOUNT_ID_AQUI'
}, indent=2), encoding='utf-8')
print(f'Credenciais salvas em: {config_path}')
"
```

Substitua `TOKEN_AQUI` e `ACCOUNT_ID_AQUI` pelos valores reais antes de executar.

Informe ao usuário o caminho onde o arquivo foi salvo.

---

## Passo 5 — Verificar a conexão

1. Leia o script com o Read tool: `../scripts/setup_check.py` — anote o caminho absoluto
2. Execute diretamente: `python3 <caminho_absoluto>`

Se ambos os testes passarem (`Token valido` e `Conta acessivel`), informe que a configuração está completa e o usuário já pode usar todos os skills do plugin.

**Se o token falhar:** volte ao Passo 2 e gere um novo token no Explorador da Graph API. Tokens do Explorer duram ~1 hora; para tokens duradouros, o usuário precisa configurar um app no Meta Developers.

**Se a conta falhar:** verifique se o ID está no formato `act_XXXXXXXXX` e se o token tem as permissões `ads_read` e `ads_management`.
