// static/js/converter.js

const previewContainer = document.getElementById("previewContainer");
// Pega os arquivos salvos na sessão do navegador
const pdfFiles = JSON.parse(sessionStorage.getItem("pdfFiles")) || [];

if (pdfFiles.length === 0) {
  previewContainer.innerHTML = "<p>Nenhum arquivo PDF encontrado. Volte para a página de upload.</p>";
} else {
  // Cria a pré-visualização para cada arquivo
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

  // Mostra um indicador de carregamento (opcional, mas bom para o usuário)
  document.body.style.cursor = 'wait';
  const convertBtn = document.querySelector('.convert-btn');
  convertBtn.disabled = true;
  convertBtn.textContent = 'CONVERTENDO...';

  // Cria um objeto FormData para agrupar todos os arquivos
  const formData = new FormData();

  // Usa Promise.all para garantir que todos os arquivos sejam processados antes do envio
  const filePromises = pdfFiles.map(fileData => {
    return fetch(fileData.dataUrl)
      .then(res => res.blob())
      .then(blob => {
        // Adiciona cada arquivo ao FormData. O '[]' no nome é importante!
        formData.append('files[]', blob, fileData.name);
      });
  });

  // Quando todos os arquivos forem adicionados ao formData...
  Promise.all(filePromises).then(() => {
    // ...enviamos o pacote de arquivos para o backend
    fetch('/', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) throw new Error("Falha na conversão no servidor.");
      // O backend agora responde com um blob do tipo ZIP
      return response.blob(); 
    })
    .then(zipBlob => {
      // Cria um link de download para o arquivo ZIP
      const url = window.URL.createObjectURL(zipBlob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Gera o nome do arquivo ZIP com a data
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getFullYear()}`;
      a.download = `Extracao_Notas_${dateStr}.zip`;
      
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      // Limpa a sessão e redireciona (opcional)
      sessionStorage.removeItem("pdfFiles");
      // window.location.href = "/";
    })
    .catch(err => {
        console.error(err);
        alert("Ocorreu um erro: " + err.message);
    })
    .finally(() => {
        // Restaura o botão e o cursor
        document.body.style.cursor = 'default';
        convertBtn.disabled = false;
        convertBtn.textContent = 'CONVERTER PARA XML';
    });
  });
}