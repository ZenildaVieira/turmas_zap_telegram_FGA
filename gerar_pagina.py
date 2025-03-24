from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Configurar o Selenium (Substitua pelo caminho correto do WebDriver)
service = Service("/caminho/para/chromedriver")  # Ajuste o caminho para o ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa sem abrir o navegador
driver = webdriver.Chrome(service=service, options=options)

# Acessar o site e extrair turmas
driver.get("URL_DO_SITE_COM_TURMAS")
time.sleep(5)  # Esperar a página carregar (ajuste conforme necessário)

# Pegando os nomes das turmas (ajuste conforme o site)
turma_elements = driver.find_elements(By.CLASS_NAME, "classe_da_turma")  # Ajuste o seletor
turmas = [turma.text for turma in turma_elements if turma.text]

driver.quit()  # Fechar o Selenium

# Criar HTML dinâmico com as turmas
html_content = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Turmas e Links</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 20px;
        }}
        #container {{
            max-width: 600px;
            margin: auto;
        }}
        .turma {{
            border: 1px solid #ccc;
            padding: 10px;
            margin: 10px 0;
            text-align: left;
        }}
        .turma input {{
            width: 100%;
            padding: 5px;
            margin-top: 5px;
        }}
        .turma button {{
            margin-top: 5px;
            padding: 5px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="container">
        <h2>Turmas e Links de Grupos</h2>
        <div id="turmasContainer">
"""

# Adicionar cada turma ao HTML
for turma in turmas:
    html_content += f"""
        <div class="turma">
            <h3>{turma}</h3>
            <input type="text" id="input-{turma}" placeholder="Insira o link do grupo">
            <button onclick="addLink('{turma}')">Salvar</button>
            <div id="links-{turma}" class="links"></div>
        </div>
    """

html_content += """
    </div>
</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        loadTurmas();
    });

    function addLink(turma) {
        let input = document.getElementById(`input-${turma}`);
        let link = input.value.trim();
        if (link !== "") {
            let links = JSON.parse(localStorage.getItem(turma)) || [];
            links.push(link);
            localStorage.setItem(turma, JSON.stringify(links));
            input.value = "";
            loadLinks(turma);
        }
    }

    function loadLinks(turma) {
        let container = document.getElementById(`links-${turma}`);
        container.innerHTML = "";
        let links = JSON.parse(localStorage.getItem(turma)) || [];
        links.forEach(link => {
            let p = document.createElement("p");
            let a = document.createElement("a");
            a.href = link;
            a.textContent = link;
            a.target = "_blank";
            p.appendChild(a);
            container.appendChild(p);
        });
    }
</script>

</body>
</html>
"""

# Salvar o HTML gerado
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Página HTML gerada com sucesso! Abra 'index.html' no navegador.")
