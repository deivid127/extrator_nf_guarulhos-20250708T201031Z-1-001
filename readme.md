ve# Extrator de NFSe (PDF para XML) - Prefeitura de Guarulhos

Este é um projeto web simples, construído com Flask (Python), para extrair dados de Notas Fiscais de Serviço (NFS-e) em formato PDF, da Prefeitura de Guarulhos, e gerar um arquivo XML para download.

## Como Rodar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- VS Code (ou qualquer outro editor de texto/IDE)
- Um terminal (o terminal integrado do VS Code é perfeito)

### 1. Preparar o Ambiente
Abra o terminal no VS Code (`Ctrl+` ou `Terminal > Novo Terminal`) e execute os seguintes comandos na pasta raiz do projeto:

```bash
# 1. Criar um ambiente virtual para isolar as dependências
python3 -m venv venv

# 2. Ativar o ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# 3. Instalar as bibliotecas necessárias do arquivo requirements.txt
pip install -r requirements.txt
```

### 2. Executar a Aplicação

Com o ambiente virtual ainda ativado, execute o seguinte comando no terminal:

```bash
flask run
```

Você verá uma saída parecida com esta:
```
 * Serving Flask app 'app'
 * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
   (Press CTRL+C to quit)
```

### 3. Usar a Ferramenta
Abra seu navegador de internet (Chrome, Firefox, etc.) e acesse o endereço:
**http://127.0.0.1:5000**

Você verá a interface para upload. Selecione um arquivo PDF de uma nota fiscal de Guarulhos e clique em "Gerar XML" para fazer o download do resultado.

## **AVISO IMPORTANTE**
A lógica de extração de dados no arquivo `extrator.py` depende MUITO do layout do PDF. Os padrões de busca (expressões regulares) foram criados como exemplos genéricos. **É muito provável que você precise ajustá-los** para que correspondam exatamente ao texto e à estrutura das suas notas fiscais.