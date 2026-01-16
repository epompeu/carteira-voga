# 🚀 Guia de Início Rápido

## Instalação Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Pronto para usar!
```

## Seu Primeiro Relatório

### Opção 1: CLI (Mais Simples)

```bash
# Processar um arquivo de Renda Fixa
python cli.py -c "Seu Nome" -rf seu_arquivo.xlsx

# Ver resumo no console
python cli.py -c "Seu Nome" -rf seu_arquivo.xlsx --resumo
```

Os relatórios serão salvos em: `./relatorios/Seu_Nome_YYYYMMDD_HHMMSS/`

### Opção 2: Python Script

```python
from core import ProcessadorCarteira, AnalisadorAvancado

# Criar processador
proc = ProcessadorCarteira()

# Carregar dados
proc.carregar_renda_fixa('seu_arquivo.xlsx')

# Consolidar
proc.consolidar_carteira()

# Análises
analisador = AnalisadorAvancado(proc.carteira_consolidada)
print(analisador.analisar_diversificacao())

# Exportar
proc.exportar_para_excel('relatorio.xlsx')
```

## Formato de Arquivo Esperado

Sua planilha Excel deve ter colunas como:

| Ativo | Valor Bruto | Data Vencimento | Classe |
|-------|-------------|-----------------|--------|
| LTN 01/01/2024 | 10000 | 01/01/2024 | Tesouro |
| CDB Banco X | 5000 | 15/03/2024 | Renda Fixa |

**Importante**: O sistema detecta automaticamente as colunas, então os nomes podem variar ligeiramente.

## Categorias Suportadas

- **-rf**: Renda Fixa
- **-coe**: COE (Certificado de Operações Estruturadas)
- **-rv**: Renda Variável
- **-der**: Derivativos

## Exemplos Comuns

### Processar Múltiplas Categorias

```bash
python cli.py -c "João Silva" \
  -rf renda_fixa.xlsx \
  -coe coe.xlsx \
  -rv acoes.xlsx
```

### Apenas Gerar Excel (Sem HTML)

```bash
python cli.py -c "João Silva" -rf rf.xlsx --no-html
```

### Ver Resumo no Console

```bash
python cli.py -c "João Silva" -rf rf.xlsx --resumo
```

## Arquivos Gerados

Após executar o comando, você receberá:

- 📄 **relatorio_carteira.html** - Relatório visual completo
- 📊 **relatorio_carteira.xlsx** - Dados em Excel com múltiplas abas
- 📈 **Gráficos PNG** - Visualizações individuais

## Próximos Passos

1. ✅ Prepare seus arquivos Excel
2. ✅ Execute o comando CLI
3. ✅ Abra o relatório HTML no navegador
4. ✅ Analise os dados

## Dúvidas Frequentes

**P: Como abro o relatório HTML?**
R: Abra o arquivo `relatorio_carteira.html` em qualquer navegador web.

**P: Posso imprimir o relatório?**
R: Sim! Use Ctrl+P (ou Cmd+P) no navegador e salve como PDF.

**P: E se minha coluna tiver outro nome?**
R: O sistema tenta detectar automaticamente. Se não funcionar, renomeie para nomes padrão.

**P: Posso processar vários clientes?**
R: Sim! Execute o comando para cada cliente separadamente.

## Próxima Leitura

Para mais detalhes, consulte [README.md](README.md)

---

**Pronto para começar? Execute:**

```bash
python cli.py -c "Seu Nome" -rf seu_arquivo.xlsx --resumo
```
