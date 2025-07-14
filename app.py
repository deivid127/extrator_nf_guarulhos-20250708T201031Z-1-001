# app.py
# (O código que você enviou para processamento em lote está correto. 
# Verifique se o seu arquivo corresponde a este, principalmente nas linhas de import)

from flask import Flask, request, render_template, Response, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pdfplumber
import xml.etree.ElementTree as ET
from datetime import datetime
import io
import zipfile

# Importa as duas funções de extração de seus respectivos arquivos
from extrator import extrair_com_regras
from extrator_ai import extrair_dados_com_ia

class Config:
    DEBUG = True
    SECRET_KEY = 'chave-super-secreta'
    UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def gerar_xml(dados_nf):
    if not dados_nf: return None
    dados_completos = { 'numero_nota': dados_nf.get('numero_nota', 'N/A'), 'data_emissao': dados_nf.get('data_emissao', 'N/A'), 'codigo_servico': dados_nf.get('codigo_servico', 'N/A'), 'valor_servicos': dados_nf.get('valor_servicos', 0.0), 'iss_retido': dados_nf.get('iss_retido', 0.0), 'retencoes_federais': dados_nf.get('retencoes_federais', 0.0), }
    root = ET.Element("NotaFiscalServico");
    ET.SubElement(root, "Numero").text = str(dados_completos['numero_nota']);
    ET.SubElement(root, "DataEmissao").text = str(dados_completos['data_emissao']);
    servicos = ET.SubElement(root, "Servicos");
    ET.SubElement(servicos, "CodigoServico").text = str(dados_completos['codigo_servico']);
    ET.SubElement(servicos, "Valor").text = f"{dados_completos['valor_servicos']:.2f}";
    retencoes = ET.SubElement(root, "Retencoes");
    total_retido = dados_completos.get('iss_retido', 0.0) + dados_completos.get('retencoes_federais', 0.0);
    ET.SubElement(retencoes, "ISSRetido").text = f"{dados_completos.get('iss_retido', 0.0):.2f}";
    ET.SubElement(retencoes, "PIS").text = "0.00";
    ET.SubElement(retencoes, "COFINS").text = "0.00";
    ET.SubElement(retencoes, "IR").text = "0.00";
    ET.SubElement(retencoes, "INSS").text = "0.00";
    ET.SubElement(retencoes, "CSLL").text = "0.00";
    ET.SubElement(retencoes, "ValorTotalRetido").text = f"{total_retido:.2f}";
    ET.indent(root, space="  ");
    return ET.tostring(root, encoding='unicode', xml_declaration=True);


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files[]')

        if not uploaded_files:
            return "Nenhum arquivo enviado!", 400

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in uploaded_files:
                if file and file.filename.lower().endswith('.pdf'):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    dados = None
                    try:
                        with pdfplumber.open(filepath) as pdf:
                            texto_completo = pdf.pages[0].extract_text() or ""
                        
                        if "guarulhos.ginfes.com.br" in texto_completo:
                            dados = extrair_com_regras(filepath)
                        else:
                            dados = extrair_dados_com_ia(filepath)
                    except Exception as e:
                        print(f"Falha ao processar o arquivo {filename}: {e}")
                        zf.writestr(f"ERRO_{filename}.txt", f"Não foi possível processar este arquivo.\nErro: {e}")
                        continue 

                    if dados:
                        xml_content = gerar_xml(dados)
                        xml_filename = f"{dados.get('numero_nota', os.path.splitext(filename)[0])}.xml"
                        zf.writestr(xml_filename, xml_content)
                    
                    os.remove(filepath)

        memory_file.seek(0)
        today_str = datetime.now().strftime('%d-%m-%Y')
        zip_filename = f"Extracao_Notas_{today_str}.zip"

        return Response(
            memory_file,
            mimetype='application/zip',
            headers={'Content-Disposition': f'attachment;filename={zip_filename}'}
        )
    # A rota GET deve servir a página de upload, não o index.html antigo
    return render_template('upload.html')

@app.route('/converter')
def converter_page():
    return render_template('converter.html')

if __name__ == '__main__':
    app.run()