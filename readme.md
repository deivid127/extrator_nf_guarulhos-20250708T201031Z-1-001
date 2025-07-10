# Extrator de NFSe com Inteligência Artificial

Este projeto utiliza uma interface web e um modelo de Inteligência Artificial (LayoutLM) para extrair dados de qualquer Nota Fiscal de Serviço (NFS-e) em formato PDF e gerar um arquivo XML com as informações.

## Funcionalidades
- Interface web simples para upload de arquivos.
- Pré-visualização do PDF enviado diretamente no navegador.
- Extração de dados flexível e universal usando um modelo de IA (Document Question Answering).
- Geração de arquivo XML padronizado para download.

## Pré-requisitos
- Python 3.8 ou superior.
- **Para usuários Windows:** Você **precisa** ter os utilitários externos `Poppler` e `Tesseract-OCR` instalados. O código está configurado para procurá-los nos caminhos padrão (`C:\poppler\...` e `C:\Program Files\Tesseract-OCR`). Certifique-se de que os caminhos no topo do arquivo `extrator.py` correspondem à sua instalação.

## Instalação e Setup

1.  **Clone ou baixe os arquivos do projeto.**

2.  **Abra um terminal** na pasta raiz do projeto.

3.  **Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    ```

4.  **Ative o ambiente virtual:**
    - No Windows (PowerShell):
      ```powershell
      .\venv\Scripts\activate
      ```
      *(Se encontrar um erro de política de execução, rode `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` primeiro).*
    - No macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

5.  **Instale todas as dependências** com um único comando, usando o arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Esta etapa pode demorar, pois fará o download de bibliotecas grandes como PyTorch e Transformers).*

## Como Executar

1.  Com o ambiente virtual ativado, inicie o servidor Flask com o comando robusto:
    ```bash
    python -m flask run
    ```

2.  **Aguarde o download do modelo de IA.** Na primeira vez que você rodar, o programa irá baixar o modelo de IA da internet, o que pode levar vários minutos. Aguarde até que a mensagem `[INFO AI] Modelo de IA carregado com sucesso` apareça no terminal.

3.  **Acesse a aplicação** no seu navegador pelo endereço: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Considerações Importantes
- **Desempenho:** A extração com IA é mais lenta que um sistema de regras. O processamento de uma nota pode levar de 5 a 30 segundos, dependendo do seu computador.
- **Precisão:** A IA é muito flexível, mas não é 100% perfeita. Para layouts muito complexos ou de baixa qualidade, alguns campos podem não ser extraídos corretamente.
- **Hardware:** O processo exige um uso considerável de CPU e memória RAM.