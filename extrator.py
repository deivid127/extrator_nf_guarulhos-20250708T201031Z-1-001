# extrator.py

import openai
import json
import os
import re

# --- Configuração dos Programas Externos ---
try:
    caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
except Exception:
    pass
CAMINHO_POPPLER = r"C:\poppler\Release-24.08.0-0\bin"
# -----------------------------------------------------------


# Carregamento do modelo de IA
print("[INFO AI] Carregando modelo de IA de Documentos...")
try:
    QA_PIPELINE = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
    print("[INFO AI] Modelo de IA carregado com sucesso.")
except Exception as e:
    QA_PIPELINE = None
    print(f"[ERRO AI] Não foi possível carregar o modelo de IA: {e}")


# --- PROMPT CORRIGIDO COM OS COLCHETES DUPLOS ---
PROMPT_TEMPLATE = """
Você é um assistente especialista em extrair dados estruturados de notas fiscais de serviço (NFS-e) brasileiras.
Sua tarefa é analisar o texto bruto de uma NFS-e que será fornecido e retornar os dados em um formato JSON limpo.

O formato de saída JSON deve ser o seguinte:
{{
  "numero_nota": "extraia o número da nota",
  "data_emissao": "extraia a data e hora completas da emissão no formato DD/MM/AAAA HH:MM:SS",
  "valor_servicos": "extraia o valor total dos serviços como um número com ponto decimal, por exemplo, 350.00",
  "codigo_servico": "extraia o código completo e a descrição do serviço",
  "iss_retido": "extraia o valor do ISS Retido como um número com ponto decimal",
  "retencoes_federais": "extraia o valor total das retenções federais (PIS, COFINS, IR, CSLL) como um número com ponto decimal"
}}

Se um campo específico não for encontrado no texto, o valor no JSON deve ser "N/A".
Sua resposta deve conter APENAS o objeto JSON, sem nenhum texto adicional.

Aqui está o texto extraído do PDF:
---
{texto_do_pdf}
---
"""

def extrair_dados_com_gpt(texto_pdf: str):
    if not openai.api_key:
        raise ValueError("Chave da API da OpenAI não configurada.")
    
    prompt_final = PROMPT_TEMPLATE.format(texto_do_pdf=texto_pdf)
    print("[INFO] Enviando requisição para a API da OpenAI...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especialista em extração de dados."},
                {"role": "user", "content": prompt_final}
            ]
        )
        
        resposta_bruta = response.choices[0].message.content
        dados_extraidos = json.loads(resposta_bruta)
        
        for key in ['valor_servicos', 'iss_retido', 'retencoes_federais']:
            valor = dados_extraidos.get(key)
            if isinstance(valor, str) and valor != "N/A":
                valor_limpo = re.sub(r'[^\d.]', '', valor.replace(',', '.'))
                dados_extraidos[key] = float(valor_limpo) if valor_limpo else 0.0
            elif not isinstance(valor, (int, float)):
                 dados_extraidos[key] = 0.0

        return dados_extraidos

    except Exception as e:
        print(f"ERRO CRÍTICO no extrator.py: {e}")
        raise e