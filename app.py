# app.py

from flask import Flask, request, render_template, Response, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import openai
import pdfplumber
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import traceback # Importamos a biblioteca de traceback

load_dotenv()
from extrator import extrair_dados_com_gpt # Supondo que o extrator de IA agora se chama extrator.py

class Config:
    DEBUG = True
    SECRET_KEY = 'gpt-secret-key-final'
    UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

# A função gerar_xml pode continuar aqui ou no extrator, sem problemas.
def gerar_xml(dados_nf):
    # ... (código da função gerar_xml igual ao anterior) ...
    if not dados_nf: return None;
    dados_completos = { 'numero_nota': dados_nf.get('numero_nota', 'N/A'), 'data_emissao': dados_nf.get('data_emissao', 'N/A'), 'codigo_servico': dados_nf.get('codigo_servico', 'N/A'), 'valor_servicos': dados_nf.get('valor_servicos', 0.0), 'iss_retido': dados_nf.get('iss_retido', 0.0), 'retencoes_federais': dados_nf.get('retencoes_federais', 0.0), };
    root = ET.Element("NotaFiscalServico");
    ET.SubElement(root, "Numero").text = str(dados_completos['numero_nota']);
    ET.SubElement(root, "DataEmissao").text = str(dados_completos['data_emissao']);
    servicos = ET.SubElement(root, "Servicos");
    ET.SubElement(servicos, "CodigoServico").text = str(dados_completos['codigo_servico']);
    ET.SubElement(servicos, "Valor").text = f"{dados_completos['valor_servicos']:.2f}";
    retencoes = ET.SubElement(root, "Retencoes");
    total_retido = dados_completos['iss_retido'] + dados_completos['retencoes_federais'];
    ET.SubElement(retencoes, "ISSRetido").text = f"{dados_completos['iss_retido']:.2f}";
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
        # ... (código de verificação do arquivo igual ao anterior) ...
        if 'file' not in request.files or not request.files['file'].filename: flash("Nenhum arquivo PDF válido selecionado!"); return redirect(request.url)
        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'): flash("Formato de arquivo inválido."); return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            with pdfplumber.open(filepath) as pdf:
                texto_completo = ""
                for page in pdf.pages:
                    texto_completo += page.extract_text() + "\n"
            
            if not texto_completo.strip():
                flash("Não foi possível ler o texto deste PDF."); return redirect(request.url)

            dados = extrair_dados_com_gpt(texto_completo)
            
            if dados:
                xml_content = gerar_xml(dados)
                numero_nota = dados.get("numero_nota", "sem_numero")
                return Response(xml_content, mimetype='application/xml', headers={'Content-Disposition': f'attachment;filename=NF_{numero_nota}.xml'})
            else:
                flash("A IA não retornou dados válidos.")
                return redirect(request.url)
        except Exception as e:
            # --- BLOCO DE EXCEÇÃO ATUALIZADO ---
            print("\n" + "#"*25 + " ERRO CAPTURADO PELO APP.PY " + "#"*25)
            # Imprime o traceback completo no terminal para vermos a causa raiz
            traceback.print_exc()
            print("#"*73 + "\n")
            flash(f"Ocorreu um erro inesperado. Verifique o terminal para detalhes.")
            return redirect(request.url)
            # ------------------------------------
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template('upload.html')

@app.route('/converter')
def converter():
    return render_template('converter.html')

if __name__ == '__main__':
    app.run()