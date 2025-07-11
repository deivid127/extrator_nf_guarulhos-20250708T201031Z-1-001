const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
let selectedFiles = [];

fileInput.addEventListener('change', () => {
  const files = Array.from(fileInput.files);
  handleFiles(files);
});

function handleDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files);
  handleFiles(files);
}

function handleFiles(files) {
  const newPDFs = files.filter(file => file.type === "application/pdf");

  const readerPromises = newPDFs.map(file => {
    return new Promise(resolve => {
      const reader = new FileReader();
      reader.onload = () => {
        resolve({ name: file.name, dataUrl: reader.result });
      };
      reader.readAsDataURL(file);
    });
  });

  Promise.all(readerPromises).then(results => {
    selectedFiles = selectedFiles.concat(results);
    salvarArquivosNaSessao();
    renderFiles();
    fileInput.value="";
  });
}

function renderFiles() {
  fileList.innerHTML = "";
  selectedFiles.forEach((file, index) => {
    const li = document.createElement("li");

    li.innerHTML = `
      📄 ${file.name}
      <button class="remove-btn" onclick="removerArquivo(${index})">×</button>
    `;

    fileList.appendChild(li);
  });
}

function removerArquivo(index) {
  selectedFiles.splice(index, 1);
  salvarArquivosNaSessao();
  renderFiles();
}

function salvarArquivosNaSessao() {
  sessionStorage.setItem("pdfFiles", JSON.stringify(selectedFiles));
}

function carregarArquivosDaSessao() {
  const dados = sessionStorage.getItem("pdfFiles");
  if (dados) {
    selectedFiles = JSON.parse(dados);
    renderFiles();
  }
}

function goToNext() {
  if (selectedFiles.length === 0) {
    alert("Selecione ao menos um arquivo PDF.");
    return;
  }

  sessionStorage.setItem("pdfFiles", JSON.stringify(selectedFiles));
  window.location.href = "converter.html";
}

window.addEventListener("DOMContentLoaded", carregarArquivosDaSessao);

