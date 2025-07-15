const previewContainer = document.getElementById("previewContainer");
const pdfFiles = JSON.parse(sessionStorage.getItem("pdfFiles")) || [];

if (pdfFiles.length === 0) {
  previewContainer.innerHTML = "<p>Nenhum arquivo PDF encontrado.</p>";
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

  // Apenas o primeiro arquivo para exemplo
  const fileData = pdfFiles[0];
  fetch(fileData.dataUrl)
    .then(res => res.blob())
    .then(blob => {
      const formData = new FormData();
      formData.append('file', blob, fileData.name);

      fetch('/', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) throw new Error("Falha na conversão.");
        return response.blob();
      })
      .then(xmlBlob => {
        const url = window.URL.createObjectURL(xmlBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'nota.xml';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(err => alert(err.message));
    });
}

function voltarParaUpload() {
  // Redireciona para a página upload.html
  window.location.href = "{{ url_for('upload') }}";
}
