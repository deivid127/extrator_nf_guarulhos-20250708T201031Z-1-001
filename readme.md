# Extrator Híbrido de Dados de NFS-e

Este projeto é uma aplicação web construída com Flask (Python) que extrai dados de Notas Fiscais de Serviço (NFS-e) em formato PDF e gera um arquivo XML com as informações.

A principal característica deste sistema é sua **arquitetura híbrida e inteligente**, que combina dois motores de extração para garantir o melhor equilíbrio entre precisão e flexibilidade.

## Arquitetura Híbrida

O sistema utiliza um roteador inteligente para analisar cada PDF e decidir qual o melhor motor de extração a ser utilizado:

1.  **Motor de Regras (`extrator.py`):**
    * **O que faz:** Utiliza um conjunto de regras de extração (Expressões Regulares - Regex) feitas sob medida para layouts de PDF específicos e conhecidos.
    * **Vantagens:** Extremamente rápido, 100% preciso e de custo zero, pois o processamento é local.
    * **Uso Ideal:** Para os tipos de notas fiscais que são processados com mais frequência e cujo layout não muda (ex: notas de um fornecedor ou prefeitura específica).

2.  **Motor de IA (`extrator_ai.py`):**
    * **O que faz:** Utiliza a API da OpenAI (modelos GPT) para analisar o conteúdo do PDF e extrair os dados. Ele "lê" o documento e responde a perguntas sobre as informações contidas nele.
    * **Vantagens:** Incrivelmente flexível, capaz de extrair dados de uma vasta gama de layouts desconhecidos sem precisar de regras pré-programadas.
    * **Uso Ideal:** Para qualquer nota fiscal de um formato novo ou inesperado.

O `app.py` funciona como o "roteador", identificando o PDF e direcionando-o para o motor mais adequado, oferecendo o melhor dos dois mundos.

## Pré-requisitos

Para que o sistema funcione completamente (incluindo o motor de IA), alguns programas externos são necessários.

1.  **Python 3.8+**
2.  **Poppler:** Utilitário necessário para converter PDFs em imagens para a IA.
    * **Instalação (Windows):** Baixe a versão mais recente [aqui](https://github.com/oschwartz10612/poppler-windows/releases/) e extraia para um local permanente (ex: `C:\poppler`).
3.  **Tesseract-OCR:** Motor de Reconhecimento Óptico de Caracteres, usado como um auxílio para a IA.
    * **Instalação (Windows):** Baixe e instale a partir do [instalador oficial](https://github.com/UB-Mannheim/tesseract/wiki). Durante a instalação, adicione o suporte ao idioma "Portuguese".
4.  **Chave de API da OpenAI:** É necessário ter uma conta na OpenAI e uma chave de API para usar o motor de IA.

## Configuração do Projeto

Siga estes passos para configurar o ambiente de desenvolvimento.

**1. Crie um Ambiente Virtual**

No terminal, na pasta raiz do projeto, execute:
```bash
python -m venv venv
```

**2. Ative o Ambiente Virtual**

* No Windows (PowerShell):
    ```powershell
    .\venv\Scripts\activate
    ```
    *(Se encontrar um erro de política de execução, rode `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` primeiro).*

* No macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

**3. Instale as Dependências**

Crie um arquivo `requirements.txt` com o seguinte conteúdo:
```text
Flask
openai
python-dotenv
pdfplumber
pdf2image
pytesseract
```
Em seguida, instale tudo com um único comando:
```bash
pip install -r requirements.txt
```

**4. Configure as Variáveis de Ambiente e Caminhos**

* **Chave de API:** Crie um arquivo chamado `.env` na raiz do projeto e coloque sua chave da OpenAI nele:
    ```
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```
    *(Lembre-se de adicionar `.env` ao seu arquivo `.gitignore` para não expor sua chave!)*

* **Caminhos do Poppler e Tesseract (Para Usuários sem permissão de Administrador):**
    Abra o arquivo `extrator_ai.py` e certifique-se de que os caminhos no topo do arquivo correspondem exatamente aos locais onde você instalou o Poppler e o Tesseract na sua máquina.
    ```python
    # Exemplo dentro de extrator_ai.py
    caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    CAMINHO_POPPLER = r"C:\poppler\Release-24.08.0-0\bin"
    ```

## Como Executar

Com o ambiente virtual `(venv)` ativado, inicie o servidor Flask com o seguinte comando:
```bash
python -m flask run
```
Na primeira vez, a aplicação pode demorar um pouco para iniciar enquanto baixa o modelo de IA. Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) no seu navegador.

## Manutenção e Expansão

Se você precisar adicionar suporte para um novo layout de nota fiscal de forma precisa (sem usar a IA), você pode expandir o **Motor de Regras**:
1.  Abra o arquivo `extrator.py`.
2.  Crie um novo dicionário de regras (ex: `REGRAS_SAO_PAULO`).
3.  Crie uma nova função de extração (ex: `extrair_com_perfil_sao_paulo`).
4.  No `app.py`, adicione um novo `elif` no roteador para detectar e chamar sua nova função.