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

    document.body.style.cursor = 'wait';
    const convertBtn = document.querySelector('.convert-btn');
    convertBtn.disabled = true;
    convertBtn.textContent = 'CONVERTENDO...';

    const formData = new FormData();

    const filePromises = pdfFiles.map(fileData => {
        return fetch(fileData.dataUrl)
            .then(res => res.blob())
            .then(blob => {
                formData.append('files[]', blob, fileData.name);
            });
    });

    Promise.all(filePromises).then(() => {
        fetch('/processar_notas', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text || "Falha na conversão no servidor.") });
            }
            return response.blob(); 
        })
        .then(zipBlob => {
            const url = window.URL.createObjectURL(zipBlob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            a.download = `Extracao_XML.zip`; 
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            sessionStorage.removeItem("pdfFiles");
        })
        .catch(err => {
            console.error(err);
            alert("Ocorreu um erro durante a conversão: " + err.message);
        })
        .finally(() => {
            document.body.style.cursor = 'default';
            convertBtn.disabled = false;
            convertBtn.textContent = 'CONVERTER PARA XML';
        });
    });
}