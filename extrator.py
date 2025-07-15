# extrator.py

import re
import pdfplumber

# --- PERFIL 1: REGRAS PARA NOTA DE GUARULHOS (ANTIGA) ---
REGRAS_GUARULHOS = {
    'numero_nota': r"NFS-e\s+(\d+)\s+Código de Verificação",
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
            for page in pdf.pages:
                texto_pagina = page.extract_text(layout=True)
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"

        for nome_campo, regra_regex in REGRAS_GUARULHOS.items():
            match = re.search(regra_regex, texto_completo, re.DOTALL)
            if match:
                valor_bruto = " ".join(match.group(1).strip().split())
                if nome_campo in CAMPOS_NUMERICOS:
                    # Converte o valor para float
                    valor_limpo = valor_bruto.replace('.', '').replace(',', '.')
                    dados[nome_campo] = float(valor_limpo) if valor_limpo else 0.0
                else:
                    dados[nome_campo] = valor_bruto
    except Exception as e:
        print(f"[ERRO no Motor de Regras] {e}")
        return None
        
    return dados