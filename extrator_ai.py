# extrator_ai.py

import re
from transformers import pipeline
from pdf2image import convert_from_path
import pytesseract

# --- Configuração dos Programas Externos ---
try:
    caminho_tesseract = r"C:\Users\usrlabecon\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
except Exception:
    pass
CAMINHO_POPPLER = r"C:\poppler-24.08.0\Library\bin"
# -----------------------------------------------------------

# Carregamento do modelo de IA
print("[INFO AI] Carregando modelo de IA de Documentos...")
try:
    QA_PIPELINE = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
    print("[INFO AI] Modelo de IA carregado com sucesso.")
except Exception as e:
    QA_PIPELINE = None
    print(f"[ERRO AI] Não foi possível carregar o modelo de IA: {e}")

def extrair_dados_com_ia(caminho_do_pdf):
    if not QA_PIPELINE:
        raise RuntimeError("O pipeline de IA não está disponível.")
    try:
        imagem_pil = convert_from_path(caminho_do_pdf, poppler_path=CAMINHO_POPPLER, first_page=1, dpi=200)[0]
        perguntas = {
            'numero_nota': "Qual é o número da nota fiscal?",
            'data_emissao': "Qual a data e hora da emissão?",
            'valor_servicos': "Qual o valor total da nota fiscal?",
            'codigo_servico': "Qual o código do serviço?",
        }
        dados_extraidos = {}
        for nome_campo, pergunta in perguntas.items():
            resultado = QA_PIPELINE(image=imagem_pil, question=pergunta)
            dados_extraidos[nome_campo] = resultado[0]['answer'] if resultado else "N/A"

        # Limpeza e conversão dos dados
        CAMPOS_NUMERICOS = ['valor_servicos']
        for campo in CAMPOS_NUMERICOS:
            valor = dados_extraidos.get(campo, "0")
            if valor and any(char.isdigit() for char in valor):
                valor_str = re.sub(r'[^\d,]', '', valor).replace(',', '.')
                dados_extraidos[campo] = float(valor_str) if valor_str else 0.0
            else:
                dados_extraidos[campo] = 0.0
        return dados_extraidos
    except Exception as e:
        print(f"ERRO CRÍTICO DURANTE A EXTRAÇÃO COM IA: {e}")
        return None