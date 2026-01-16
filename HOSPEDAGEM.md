# 🚀 Carteira VOGA - Guia de Hospedagem

## Opções de Hospedagem Gratuita

### 1. **Render (Recomendado)**

**Vantagens:**
- ✅ Gratuito
- ✅ Deploy automático via Git
- ✅ Suporta Streamlit nativamente
- ✅ HTTPS incluído
- ✅ Subdomínio gratuito

**Passos:**

1. Criar repositório no GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/carteira-voga.git
git push -u origin main
```

2. Ir para https://render.com
3. Conectar conta GitHub
4. Criar novo "Web Service"
5. Selecionar repositório
6. Configurar:
   - **Name:** carteira-voga
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app_voga.py --server.port=10000 --server.address=0.0.0.0`
7. Deploy!

**URL:** https://carteira-voga.onrender.com

---

### 2. **Railway**

**Vantagens:**
- ✅ Gratuito (com crédito mensal)
- ✅ Deploy simples
- ✅ Suporta Streamlit

**Passos:**

1. Ir para https://railway.app
2. Conectar GitHub
3. Selecionar repositório
4. Railway detectará automaticamente
5. Configurar variáveis de ambiente se necessário
6. Deploy automático!

**URL:** https://carteira-voga.railway.app

---

### 3. **Heroku (Pago, mas com free tier limitado)**

**Passos:**

1. Instalar Heroku CLI
2. Login: `heroku login`
3. Criar app: `heroku create carteira-voga`
4. Deploy: `git push heroku main`

---

## Configuração Pré-Deploy

### 1. Atualizar requirements.txt
```bash
pip freeze > requirements.txt
```

### 2. Criar .streamlit/config.toml
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false

[server]
maxUploadSize = 200
```

### 3. Criar Procfile
```
web: streamlit run app_voga.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Passo a Passo Completo (Render)

### 1. Preparar Repositório Git

```bash
cd /home/ubuntu/carteira_analyzer

# Inicializar git
git init
git config user.email "seu-email@example.com"
git config user.name "Seu Nome"

# Adicionar arquivos
git add .
git commit -m "Carteira VOGA - Initial Release"
```

### 2. Criar Repositório no GitHub

1. Ir para https://github.com/new
2. Nome: `carteira-voga`
3. Descrição: "Análise profissional de carteiras de investimentos"
4. Público
5. Criar

### 3. Fazer Push para GitHub

```bash
git remote add origin https://github.com/seu-usuario/carteira-voga.git
git branch -M main
git push -u origin main
```

### 4. Deploy no Render

1. Ir para https://render.com
2. Sign up com GitHub
3. Autorizar Render
4. Dashboard → New → Web Service
5. Conectar repositório
6. Configurar:
   - **Name:** carteira-voga
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app_voga.py --server.port=10000 --server.address=0.0.0.0`
   - **Instance Type:** Free
7. Create Web Service

### 5. Aguardar Deploy

- Render fará build e deploy automaticamente
- Pode levar 2-5 minutos
- URL será gerada automaticamente

---

## Domínio Customizado (Opcional)

### Usando Render com Domínio Customizado

1. No Render Dashboard
2. Selecionar seu Web Service
3. Settings → Custom Domain
4. Adicionar seu domínio
5. Seguir instruções de DNS

---

## Monitoramento

### Logs no Render

1. Dashboard → Seu Web Service
2. Logs → View All Logs
3. Monitorar erros em tempo real

### Reiniciar Aplicação

1. Dashboard → Seu Web Service
2. Manual Deploy → Deploy latest commit

---

## Troubleshooting

### Erro: "ModuleNotFoundError"
- Verificar requirements.txt
- Executar: `pip install -r requirements.txt` localmente

### Erro: "Port already in use"
- Render gerencia portas automaticamente
- Usar `$PORT` no comando

### Aplicação lenta
- Pode ser free tier
- Upgrade para paid tier se necessário

### Upload de arquivos não funciona
- Verificar limite em config.toml: `maxUploadSize = 200`
- Aumentar se necessário

---

## Backup e Segurança

### Backup do Código
```bash
git push origin main
```

### Segurança
- ✅ Sem armazenamento de dados
- ✅ Sem banco de dados
- ✅ Sem API keys expostas
- ✅ HTTPS automático

---

## Próximos Passos

1. ✅ Preparar repositório Git
2. ✅ Fazer push para GitHub
3. ✅ Conectar Render
4. ✅ Deploy automático
5. ✅ Compartilhar URL

---

**Suporte:** Para dúvidas, consulte a documentação do Render em https://render.com/docs
