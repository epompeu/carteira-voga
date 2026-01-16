# 🚀 Deploy Rápido - Carteira VOGA

## Em 5 Minutos para o Ar!

### Opção 1: Render (Mais Fácil) ⭐

#### Pré-requisitos:
- Conta GitHub
- Conta Render (gratuita)

#### Passos:

1. **Fazer Fork ou Criar Repositório**
   ```bash
   # Se tiver Git instalado localmente:
   git clone https://github.com/seu-usuario/carteira-voga.git
   cd carteira-voga
   git push origin main
   ```

2. **Ir para Render**
   - Abra https://render.com
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub

3. **Configurar Deployment**
   - **Name:** carteira-voga
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app_voga.py --server.port=10000 --server.address=0.0.0.0`
   - **Instance Type:** Free
   - Clique em "Create Web Service"

4. **Aguardar Deploy**
   - Render fará build automaticamente
   - Levará 2-5 minutos
   - Você receberá uma URL como: `https://carteira-voga.onrender.com`

✅ **Pronto!** Seu site está no ar!

---

### Opção 2: Railway

1. Ir para https://railway.app
2. Clique em "Login with GitHub"
3. Selecione seu repositório
4. Railway detecta automaticamente
5. Deploy automático!

---

### Opção 3: Heroku (Requer Cartão)

```bash
heroku login
heroku create carteira-voga
git push heroku main
```

---

## Estrutura do Projeto

```
carteira-voga/
├── app_voga.py                 # Aplicação principal
├── requirements.txt            # Dependências
├── Procfile                    # Configuração de deploy
├── .streamlit/
│   └── config.toml            # Configuração Streamlit
├── core/                       # Módulos principais
│   ├── parsers_relatorios.py
│   ├── analisador_relatorios.py
│   ├── gerador_excel.py
│   └── ...
├── assets/
│   └── logo.png               # Logomarca VOGA
└── README.md                  # Documentação
```

---

## Testando Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
streamlit run app_voga.py

# Acessar em http://localhost:8501
```

---

## Variáveis de Ambiente (Se Necessário)

Render suporta variáveis de ambiente. Adicione em:
Settings → Environment

Exemplo:
```
STREAMLIT_SERVER_PORT=10000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Domínio Customizado

### Render:
1. Web Service → Settings
2. Custom Domain
3. Adicionar seu domínio
4. Seguir instruções de DNS

### Exemplo:
- Seu domínio: `carteira.voga.com.br`
- Apontado para: `carteira-voga.onrender.com`

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Build falha | Verificar requirements.txt |
| App não inicia | Ver logs em Render Dashboard |
| Upload não funciona | Aumentar `maxUploadSize` em config.toml |
| Lento | Pode ser free tier, upgrade se necessário |

---

## Monitoramento

### Render Dashboard:
- Logs em tempo real
- Status da aplicação
- Histórico de deploys
- Reiniciar aplicação

---

## Próximas Melhorias

- [ ] Adicionar domínio customizado
- [ ] Configurar alertas de erro
- [ ] Adicionar analytics
- [ ] Backup automático
- [ ] Cache de dados

---

## Suporte

- 📖 Documentação: `/HOSPEDAGEM.md`
- 🐛 Issues: GitHub
- 💬 Comunidade: Render Community

---

**Versão:** 1.0  
**Última atualização:** Janeiro 2026
