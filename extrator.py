# extrator.py

import re
import pdfplumber

# Regras precisas e testadas para o layout específico de Guarulhos
REGRAS_GUARULHOS = {
    'numero_nota': r"Número da\s+NFS-e\s+(\d+)",
    'data_emissao': r"Data e Hora da Emissão\s+([\d/]+\s*[\d:]+)",
    'codigo_servico': r"Código do Serviço / Atividade\s+([^\n]*)",
    'valor_servicos': r"Valor dos Serviços R\$\s*([\d\.,]+)",
    'iss_retido': r"\(-\) ISS Retido\s+([\d\.,]+)",
    'retencoes_federais': r"\(-\) Retenções Federais\s+([\d\.,]+)"
}

CAMPOS_NUMERICOS = ['valor_servicos', 'iss_retido', 'retencoes_federais']

def extrair_com_regras(caminho_do_pdf):
    """Extrai dados usando as regras específicas para o layout de Guarulhos."""
    texto_completo = ""
    dados = {}
    try:
        with pdfplumber.open(caminho_do_pdf) as pdf:
            # Concatena o texto de todas as páginas para garantir
            for page in pdf.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"

        for nome_campo, regra_regex in REGRAS_GUARULHOS.items():
            match = re.search(regra_regex, texto_completo, re.DOTALL)
            if match:
                valor_bruto = " ".join(match.group(1).strip().split())
                if nome_campo in CAMPOS_NUMERICOS:
                    dados[nome_campo] = float(valor_bruto.replace('.', '').replace(',', '.'))
                else:
                    dados[nome_campo] = valor_bruto
    except Exception as e:
        print(f"[ERRO no Motor de Regras] {e}")
        return None
    return dados