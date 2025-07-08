import pdfplumber
import re
import xml.etree.ElementTree as ET

# ==============================================================================
# PERFIL DE EXTRAÇÃO 1: NOTA FISCAL ANTIGA DE GUARULHOS (BASEADO EM REGEX)
# ==============================================================================
# No topo do seu arquivo extrator.py, substitua este dicionário:
REGRAS_GUARULHOS = {
    'numero_nota': r"NFS-e\s+(\d+)",
    'data_emissao': r"Data e Hora da Emissão\s+([\d/]+\s*[\d:]+)",
    # CORREÇÃO: A regra agora captura tudo em uma linha até encontrar uma quebra de linha.
    'codigo_servico': r"Código do Serviço / Atividade\s+([^\n]*)",
    'valor_servicos': r"Valor dos Serviços R\$\s*([\d\.,]+)",
    'iss_retido': r"\(-\) ISS Retido\s+([\d\.,]+)",
    'retencoes_federais': r"\(-\) Retenções Federais\s+([\d\.,]+)"
}

def _extrair_com_perfil_guarulhos(texto_completo):
    """Extrai dados usando as regras específicas para o layout antigo de Guarulhos."""
    dados = {}
    CAMPOS_NUMERICOS = ['valor_servicos', 'iss_retido', 'retencoes_federais']

    for nome_campo, regra_regex in REGRAS_GUARULHOS.items():
        match = re.search(regra_regex, texto_completo, re.DOTALL)
        if match:
            valor_bruto = " ".join(match.group(1).strip().split())
            if nome_campo in CAMPOS_NUMERICOS:
                dados[nome_campo] = float(valor_bruto.replace('.', '').replace(',', '.'))
            else:
                dados[nome_campo] = valor_bruto
    return dados

# ==============================================================================
# PERFIL DE EXTRAÇÃO 2: NOTA FISCAL PADRÃO NACIONAL (BASEADO EM COORDENADAS)
# ==============================================================================
def _find_value_to_right_of_label(page, label):
    """Encontra um rótulo e extrai o texto em uma área à sua direita."""
    try:
        # page.search encontra todas as ocorrências do texto e suas posições
        matches = page.search(label, case=False)
        if not matches:
            return None
        
        # Pega a posição do primeiro rótulo encontrado
        first_match = matches[0]
        x0, top, x1, bottom = first_match['x0'], first_match['top'], first_match['x1'], first_match['bottom']

        # Define uma "caixa de busca" à direita do rótulo
        search_box = (x1, top, page.width, bottom + 5) # +5 para dar uma pequena margem vertical
        
        # Recorta a página para essa caixa e extrai o texto dentro dela
        cropped_text = page.crop(search_box).extract_text()
        return cropped_text.strip() if cropped_text else None
    except Exception:
        return None

def _extrair_com_perfil_nacional(pdf):
    """Extrai dados usando busca por coordenadas, ideal para layouts complexos."""
    dados = {}
    page = pdf.pages[0] # Assume que os dados principais estão na primeira página

    # Extrai o número da nota, que está abaixo do rótulo
    try:
        matches = page.search("Número da NFS-e", case=False)
        if matches:
            label_pos = matches[0]
            # Caixa de busca abaixo do rótulo
            search_box = (label_pos['x0'], label_pos['bottom'], label_pos['x1'] + 50, label_pos['bottom'] + 20)
            dados['numero_nota'] = page.crop(search_box).extract_text()
    except Exception:
        pass

    dados['data_emissao'] = _find_value_to_right_of_label(page, "Data e Hora da emissão da NFS-e")
    
    # Para o código do serviço, a abordagem de coordenada é mais complexa, regex no texto ainda é viável
    full_text = page.extract_text()
    match_servico = re.search(r"Código de Tributação Nacional\s+(.*?)(?=\s+Cód)", full_text, re.DOTALL)
    if match_servico:
        dados['codigo_servico'] = " ".join(match_servico.group(1).strip().split())
    
    match_valor = re.search(r"Valor do Serviço\s+R\$\s*([\d\.,]+)", full_text)
    if match_valor:
        dados['valor_servicos'] = match_valor.group(1)

    match_iss = re.search(r"ISSQN Retido\s+R\$\s*([\d\.,]+)", full_text)
    if match_iss:
         dados['iss_retido'] = match_iss.group(1)

    match_fed = re.search(r"IRRF, CP,CSLL - Retidos\s+R\$\s*([\d\.,]+)", full_text)
    if match_fed:
         dados['retencoes_federais'] = match_fed.group(1)
         
    # Converte os campos numéricos
    CAMPOS_NUMERICOS = ['valor_servicos', 'iss_retido', 'retencoes_federais']
    for campo in CAMPOS_NUMERICOS:
        if dados.get(campo):
            dados[campo] = float(str(dados[campo]).replace('.', '').replace(',', '.'))
            
    return dados

# ==============================================================================
# FUNÇÃO PRINCIPAL E GERADOR DE XML (ORQUESTRADORES)
# ==============================================================================
def extrair_dados_nf(caminho_do_pdf):
    """
    Função principal que identifica o layout do PDF e chama o perfil de extração correto.
    """
    try:
        with pdfplumber.open(caminho_do_pdf) as pdf:
            texto_completo = pdf.pages[0].extract_text()

            # Lógica de identificação de perfil
            if "guarulhos.ginfes.com.br" in texto_completo:
                print("[INFO] Perfil 'Guarulhos (Antigo)' detectado.")
                return _extrair_com_perfil_guarulhos(texto_completo)
            elif "portal nacional da NFS-e" in texto_completo:
                print("[INFO] Perfil 'Padrão Nacional' detectado.")
                return _extrair_com_perfil_nacional(pdf)
            else:
                print("[AVISO] Layout do PDF não reconhecido. Tentando o perfil padrão de Guarulhos.")
                return _extrair_com_perfil_guarulhos(texto_completo)

    except Exception as e:
        print(f"Erro crítico ao processar o PDF: {e}")
        return None

def gerar_xml(dados_nf):
    """Gera o XML com os dados extraídos."""
    if not dados_nf: return None
    # Preenche com valores padrão caso a extração de um campo falhe
    dados_completos = {
        'numero_nota': dados_nf.get('numero_nota', 'N/A'),
        'data_emissao': dados_nf.get('data_emissao', 'N/A'),
        'codigo_servico': dados_nf.get('codigo_servico', 'N/A'),
        'valor_servicos': dados_nf.get('valor_servicos', 0.0),
        'iss_retido': dados_nf.get('iss_retido', 0.0),
        'retencoes_federais': dados_nf.get('retencoes_federais', 0.0),
    }

    root = ET.Element("NotaFiscalServico")
    ET.SubElement(root, "Numero").text = str(dados_completos['numero_nota'])
    ET.SubElement(root, "DataEmissao").text = str(dados_completos['data_emissao'])
    
    servicos = ET.SubElement(root, "Servicos")
    ET.SubElement(servicos, "CodigoServico").text = str(dados_completos['codigo_servico'])
    ET.SubElement(servicos, "Valor").text = f"{dados_completos['valor_servicos']:.2f}"

    retencoes = ET.SubElement(root, "Retencoes")
    total_retido = dados_completos['iss_retido'] + dados_completos['retencoes_federais']
    ET.SubElement(retencoes, "ISSRetido").text = f"{dados_completos['iss_retido']:.2f}"
    ET.SubElement(retencoes, "PIS").text = "0.00"
    ET.SubElement(retencoes, "COFINS").text = "0.00"
    ET.SubElement(retencoes, "IR").text = "0.00"
    ET.SubElement(retencoes, "INSS").text = "0.00"
    ET.SubElement(retencoes, "CSLL").text = "0.00"
    ET.SubElement(retencoes, "ValorTotalRetido").text = f"{total_retido:.2f}"
    
    ET.indent(root, space="  ")
    xml_string = ET.tostring(root, encoding='unicode', xml_declaration=True)
    return xml_string