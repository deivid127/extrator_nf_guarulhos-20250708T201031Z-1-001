from flask import Flask, request, render_template, Response, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from extrator import extrair_dados_nf, gerar_xml

# Classe para centralizar as configurações da aplicação.
class Config:
    DEBUG = True  # Mude para False quando o site for para produção.
    SECRET_KEY = 'a-chave-secreta-deve-ser-longa-e-dificil-de-adivinhar'
    UPLOAD_FOLDER = 'uploads/'

# Cria a aplicação Flask
app = Flask(__name__)
# Carrega as configurações a partir da classe Config.
app.config.from_object(Config)

# Garante que a pasta de uploads exista.
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Nenhum arquivo enviado!")
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash("Nenhum arquivo selecionado!")
            return redirect(request.url)

        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                dados = extrair_dados_nf(filepath)
                
                if dados:
                    xml_content = gerar_xml(dados)
                    numero_nota = dados.get("numero_nota", "sem_numero")
                    return Response(
                        xml_content,
                        mimetype='application/xml',
                        headers={'Content-Disposition': f'attachment;filename=NF_{numero_nota}.xml'}
                    )
                else:
                    flash("Não foi possível extrair dados válidos do PDF.")
                    return redirect(request.url)

            except Exception as e:
                flash(f"Ocorreu um erro inesperado: {e}")
                return redirect(request.url)
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash("Formato de arquivo inválido. Por favor, envie um PDF.")
            return redirect(request.url)

    # Para o método GET, apenas renderiza a página de upload.
    return render_template('index.html')


# Este bloco permite rodar com "python app.py", mas o ideal é usar "flask run"
if __name__ == '__main__':
    app.run()