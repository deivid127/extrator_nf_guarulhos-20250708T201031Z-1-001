import re
import json
from transformers import pipeline
from pdf2image import convert_from_path
import pytesseract
import openai
import os
from dotenv import load_dotenv
import pdfplumber

load_dotenv()

try:
    caminho_tesseract = r"C:\Users\usrlabecon\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
except Exception:
    pass
CAMINHO_POPPLER = r"C:\poppler-24.08.0\Library\bin"

print("[INFO AI] Carregando modelo de IA de Documentos...")
try:
    QA_PIPELINE = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
    print("[INFO AI] Modelo de IA carregado com sucesso.")
except Exception as e:
    QA_PIPELINE = None
    print(f"[ERRO AI] Não foi possível carregar o modelo de IA: {e}")

PROMPT_TEMPLATE = """
Você é um assistente especialista em extrair dados estruturados de notas fiscais de serviço (NFS-e) brasileiras.
Sua tarefa é analisar o texto bruto de uma NFS-e que será fornecido e retornar os dados em um formato JSON limpo.
O formato de saída JSON deve ser o seguinte:
{{
  "numero_nota": "extraia o número da nota fiscal",
  "data_emissao": "extraia a data e hora completas da emissão no formato DD/MM/AAAA HH:MM:SS",
  "valor_servicos": "extraia o valor total dos serviços como um número com ponto decimal",
  "codigo_servico": "extraia o código completo e a descrição do serviço",
  "iss_retido": "extraia o valor do ISS Retido como um número com ponto decimal",
  "retencoes_federais": "extraia o valor total das retenções federais (PIS, COFINS, IR, CSLL) como um número com ponto decimal"
}}
Se um campo específico não for encontrado, o valor no JSON deve ser "N/A".
Sua resposta deve conter APENAS o objeto JSON, sem nenhum texto adicional.

Aqui está o texto extraído do PDF:
---
{texto_do_pdf}
---
"""

def extrair_dados_com_ia(caminho_do_pdf):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Chave da API da OpenAI não encontrada.")

    try:
        with pdfplumber.open(caminho_do_pdf) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"

        if not texto_completo.strip():
            return None

        prompt_final = PROMPT_TEMPLATE.format(texto_do_pdf=texto_completo)
        print(f"[INFO] Enviando '{os.path.basename(caminho_do_pdf)}' para a API da OpenAI...")
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Você é um assistente especialista em extração de dados JSON."}, {"role": "user", "content": prompt_final}]
        )
        
        resposta_bruta = response.choices[0].message.content
        
        try:
            dados_extraidos = json.loads(resposta_bruta)
        except json.JSONDecodeError:
            return None

        for key in ['valor_servicos', 'iss_retido', 'retencoes_federais']:
            valor = dados_extraidos.get(key)
            if isinstance(valor, str) and valor != "N/A":
                valor_limpo = re.sub(r'[^\d.]', '', valor.replace(',', '.'))
                dados_extraidos[key] = float(valor_limpo) if valor_limpo else 0.0
            elif not isinstance(valor, (int, float)):
                 dados_extraidos[key] = 0.0

        return dados_extraidos
    except Exception as e:
        print(f"ERRO CRÍTICO no extrator_ai.py: {e}")
        return None