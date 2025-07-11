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
  alert("Simulação: conversão para XML concluída!");
}
