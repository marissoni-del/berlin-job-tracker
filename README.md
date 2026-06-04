# 🗺️ Berlin Job Tracker – Mateus Andery Rissoni

Busca automática diária de vagas em Berlim alinhadas ao seu perfil:
**inglês / espanhol / português · políticas públicas · pesquisa · cooperação internacional**

---

## Como funciona

1. **scraper.py** busca vagas em Indeed, Euractiv, ImpactPool e Devex
2. **generate_html.py** gera o painel visual `dashboard.html`
3. **GitHub Actions** roda tudo automaticamente todo dia às 09:00 (Berlin)
4. O `dashboard.html` fica disponível via **GitHub Pages** — você acessa pelo navegador

---

## Configuração passo a passo (sem precisar de servidor)

### Passo 1 — Criar conta no GitHub
- Acesse [github.com](https://github.com) e crie uma conta gratuita

### Passo 2 — Criar um repositório
- Clique em **New repository**
- Nome sugerido: `berlin-job-tracker`
- Marque como **Public** (necessário para GitHub Pages gratuito)
- Clique em **Create repository**

### Passo 3 — Fazer upload dos arquivos
Faça upload de todos estes arquivos para o repositório:
```
scraper.py
generate_html.py
requirements.txt
.github/
  workflows/
    daily_search.yml
```

Para fazer o upload:
- Na página do repositório, clique em **Add file → Upload files**
- Arraste todos os arquivos e a pasta `.github`
- Clique em **Commit changes**

### Passo 4 — Ativar GitHub Pages
- No repositório, vá em **Settings → Pages**
- Em **Source**, selecione **Deploy from a branch**
- Em **Branch**, selecione `main` e pasta `/ (root)`
- Clique em **Save**
- Após alguns minutos, seu painel estará disponível em:
  `https://SEU_USUARIO.github.io/berlin-job-tracker/dashboard.html`

### Passo 5 — Testar manualmente
- Vá em **Actions** no repositório
- Clique em **Berlin Job Tracker – Daily Search**
- Clique em **Run workflow → Run workflow**
- Aguarde 2–3 minutos e abra o dashboard

### Passo 6 — Rotina automática
A partir daí, o scraper roda **todo dia às 09:00 (horário de Berlin)** automaticamente.
Você acessa o dashboard pelo navegador sempre que quiser ver as atualizações.

---

## Personalização

Para ajustar as buscas, edite `scraper.py`:

```python
# Adicionar palavras-chave de busca
SEARCH_QUERIES = [
    "policy research berlin english",
    "latin america berlin english",
    # adicione mais aqui...
]

# Palavras que qualificam uma vaga
INCLUDE_KEYWORDS = [
    "english", "policy", "research", ...
]

# Palavras que desqualificam (ex: exigem alemão fluente)
EXCLUDE_KEYWORDS = [
    "fließend deutsch",
    ...
]
```

---

## Estrutura dos arquivos

```
berlin-job-tracker/
├── scraper.py          # Busca vagas nas fontes
├── generate_html.py    # Gera o painel visual
├── requirements.txt    # Dependências Python
├── jobs_data.json      # Dados salvos (gerado automaticamente)
├── dashboard.html      # Painel visual (gerado automaticamente)
└── .github/
    └── workflows/
        └── daily_search.yml  # Automação diária
```

---

## Fontes de busca

| Fonte | Tipo | Foco |
|---|---|---|
| Indeed (RSS) | Geral | Vagas em Berlin com filtros de inglês/política |
| Euractiv Jobs | Especializado | Política europeia, inglês |
| ImpactPool | Especializado | ONGs, cooperação internacional |
| Devex | Especializado | Desenvolvimento internacional |

---

## Dúvidas?

Se o workflow falhar, vá em **Actions → ver o erro** e copie a mensagem.
Os erros mais comuns são: timeout de rede (tente rodar novamente) ou
repositório privado sem GitHub Pages ativo.
