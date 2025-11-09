from coletar_selenium import *
from datetime import datetime


data_inicio = datetime.now()
data_formatada = data_inicio.strftime("%Y-%m-%d")


print("===================================")
print(f"Início: {data_inicio}")
print("===================================")

nivel = "GRADUAÇÃO"
ano = "2025"
periodo = "1"

turmas = []
turmas = main_carregar_dados(nivel, ano, periodo)

# Criar HTML dinâmico sem links pré-preenchidos
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

# Adicionar cada turma ao HTML sem links pré-carregados
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
        // Apagar os links antigos sempre que um novo HTML for gerado
        localStorage.clear();
        setTimeout(loadAllLinks, 500);
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
        if (!container) return;

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

    function loadAllLinks() {
        let turmas = document.querySelectorAll(".turma h3");
        turmas.forEach(turmaElement => {
            let turma = turmaElement.textContent.trim();
            loadLinks(turma);
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

data_fim = datetime.now()
print(f"Fim: {data_fim}")
print("================================")
print(f"Duração do processo: {data_fim - data_inicio}")
print("====================================")
