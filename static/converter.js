// static/js/converter.js

const previewContainer = document.getElementById("previewContainer");
const pdfFiles = JSON.parse(sessionStorage.getItem("pdfFiles")) || [];

if (pdfFiles.length === 0) {
    document.querySelector('.container').innerHTML = "<p>Nenhum arquivo PDF encontrado. Por favor, volte para a página inicial para selecionar os arquivos.</p>";
} else {
    pdfFiles.forEach(file => {
        const box = document.createElement("div");
        box.className = "preview-box";
        const embed = document.createElement("embed");
        embed.src = file.dataUrl;
        embed.type = "application/pdf";
        box.appendChild(embed);
        previewContainer.appendChild(box);
    });
}

function convertToXML() {
    if (pdfFiles.length === 0) {
        alert("Nenhum arquivo PDF para converter.");
        return;
    }

    // Mostra um indicador de carregamento
    document.body.style.cursor = 'wait';
    const convertBtn = document.querySelector('.convert-btn');
    convertBtn.disabled = true;
    convertBtn.textContent = 'CONVERTENDO...';

    const formData = new FormData();

    // Usa Promise.all para garantir que todos os arquivos sejam processados antes do envio
    const filePromises = pdfFiles.map(fileData => {
        return fetch(fileData.dataUrl)
            .then(res => res.blob())
            .then(blob => {
                // Adiciona cada arquivo ao FormData. O '[]' no nome da chave é crucial!
                formData.append('files[]', blob, fileData.name);
            });
    });

    // Quando todos os arquivos forem adicionados ao formData...
    Promise.all(filePromises).then(() => {
        // ...enviamos o pacote de arquivos para a nova rota /processar_notas
        fetch('/processar_notas', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Tenta ler a mensagem de erro do servidor, se houver
                return response.text().then(text => { throw new Error(text || "Falha na conversão no servidor.") });
            }
            return response.blob(); 
        })
        .then(zipBlob => {
            const url = window.URL.createObjectURL(zipBlob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // O nome do arquivo será definido pelo backend, mas podemos colocar um padrão
            a.download = `Extracao_XML.zip`; 
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            // Limpa a sessão após o download bem-sucedido
            sessionStorage.removeItem("pdfFiles");
        })
        .catch(err => {
            console.error(err);
            alert("Ocorreu um erro durante a conversão: " + err.message);
        })
        .finally(() => {
            // Restaura o botão e o cursor
            document.body.style.cursor = 'default';
            convertBtn.disabled = false;
            convertBtn.textContent = 'CONVERTER PARA XML';
        });
    });
}