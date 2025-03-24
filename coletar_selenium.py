import pandas as pd
from datetime import datetime
import time
import re
from selenium import webdriver                              # Controla o navegador
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service      # Gerencia o GeckoDriver no Firefox
from selenium.webdriver.firefox.options import Options      # Permite definir argumentos para personalizar a execução do navegado
from webdriver_manager.firefox import GeckoDriverManager    # Automatiza o download e configuração do GeckoDriver.


def iniciar_navegador():
    # Inicia o navegador Firefox configurado para web scraping
    options = Options()                                         # Cria um objeto de opções para o navegador Firefox
    options.add_argument('--headless')                          # Executa sem interface gráfica
    options.add_argument('--disable-logging')                   # Suprime logs desnecessários
    service = Service(GeckoDriverManager().install())           # Configura o serviço com o GeckoDriverManager
                                                                # Faz o download automático da versão mais recente do driver compatível com o sistema operacional e o navegador
    return webdriver.Firefox(service=service, options=options)  # Cria e retorna o navegador configurad para uso


def coletar_dados_turmas(navegador, nivel, depto, ano, periodo):
    """
    Coleta informações das turmas de um departamento específico no SIGAA.
    
    Parâmetros:
    - navegador: Instância do WebDriver para automação do navegador.
    - nivel: Nível da turma (ex.: "Graduação", "Pós-graduação").
    - depto: Departamento responsável pelas turmas (ex.: "FGA" ou "FCTE").
    - ano: Ano das turmas a serem coletadas (ex.: "2024").
    - periodo: Período letivo (ex.: "1" ou "2").
    
    Retorna:
    - Lista de dicionários contendo as informações das turmas.
    """
    
    # URL da página do SIGAA onde as turmas estão listadas
    url = 'https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino'
    # Navegador acessa a URL definida
    navegador.get(url)

    # Preenchendo o formulário de busca na página
    # Localiza os campos pelo atributo `name` e insere o valor 
    navegador.find_element(By.NAME, 'formTurma:inputNivel').send_keys(nivel)
    navegador.find_element(By.NAME, 'formTurma:inputDepto').send_keys(depto)
    navegador.find_element(By.NAME, 'formTurma:inputAno').clear()
    navegador.find_element(By.NAME, 'formTurma:inputAno').send_keys(ano)
    navegador.find_element(By.NAME, 'formTurma:inputPeriodo').send_keys(periodo)
    navegador.find_element(By.NAME, 'formTurma:j_id_jsp_1370969402_11').click()

    # Aguarda 2 segundos para garantir que a página carregue os resultados para evitar problemas de sincronização
    time.sleep(2)

    # Localiza todas as linhas da tabela com as turmas utilizando XPath
    # As linhas estão localizadas no elemento <tbody> dentro da tabela com ID "turmasAbertas"
    linhas = navegador.find_elements(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr')
    
    # Lista para armazenar as informações coletadas de cada turma
    turmas = []
    # Variável auxiliar para armazenar o código da disciplina agrupadora
    codigo_disciplina = None
    
    # Itera sobre as linhas da tabela
    for linha in linhas:
        # Obtém o atributo "class" da linha, usado para diferenciar o tipo de dado exibido
        classe = linha.get_attribute("class")
        # Caso a linha seja um agrupador (contendo o código da disciplina)
        if classe == "agrupador":
            # Localiza e extrai o texto do elemento com a classe "tituloDisciplina"
            codigo_disciplina = linha.find_element(By.CLASS_NAME, "tituloDisciplina").text.strip()
        # Caso a linha seja de uma turma (linha par ou ímpar da tabela)
        elif classe in ("linhaPar", "linhaImpar"):
            # Localiza a coluna que contém informações sobre o local (8ª coluna da linha)
            local = linha.find_element(By.XPATH, "./td[8]").text.strip()
            
            # Filtra turmas oferecidas pela FGA
            if "FGA" in local or "FCTE" in local:
                # Extrai os dados específicos da turma utilizando a função auxiliar `extrair_dados_turma`
                turma = extrair_dados_turma(linha, codigo_disciplina)
                # Adiciona a turma à lista de turmas
                turmas.append(turma)

    # Retorna a lista de turmas coletadas
    return turmas


def extrair_dados_turma(linha, codigo_disciplina):
    """ Extrai informações detalhadas de uma única linha de uma tabela de turmas.
        Parâmetros:
            - linha: Elemento WebElement correspondente à linha de uma tabela do SIGAA.
            - codigo_disciplina: Código da disciplina ao qual a turma pertence.
        Retorna:
            - Lista com os seguintes dados:
                [código da disciplina, código da turma, código da matéria da turma, ano, 
                semestre,  dados do professor e carga horária (brutos e processados), 
                horário, vagas ofertadas, vagas ocupadas, local].
    """
    # Extrai o código da turma da coluna com a classe "turma"
    codigo_turma = linha.find_element(By.CLASS_NAME, "turma").text.strip()
    # Gera o identificador completo da matéria/turma combinando o código da disciplina e da turma
    materia_turma = f"{codigo_disciplina[:7]}{codigo_turma}"
    # Extrai o ano e o semestre do campo com a classe "anoPeriodo". O valor é separado por um ponto (ex.: "2024.1")
    ano, semestre = linha.find_element(By.CLASS_NAME, "anoPeriodo").text.strip().split(".")
    # Extrai o horário da turma, localizado na 4ª coluna da linha
    horario = linha.find_element(By.XPATH, "./td[4]").text.strip()
    # Extrai o número de vagas ofertadas, localizado na 6ª coluna
    vagas_ofertadas = int(linha.find_element(By.XPATH, "./td[6]").text.strip())
    # Extrai o número de vagas ocupadas, localizado na 7ª coluna
    vagas_ocupadas = int(linha.find_element(By.XPATH, "./td[7]").text.strip())
    # Extrai o local da turma, localizado na 8ª coluna
    local = linha.find_element(By.XPATH, "./td[8]").text.strip()
    # Extrai as informações sobre o professor e carga horária do campo com a classe "nome"
    # O atributo 'innerHTML' contém os dados em formato bruto
    prof_carga_hor = linha.find_element(By.CLASS_NAME, "nome").get_attribute('innerHTML').strip()
    # Processa os dados extraídos para identificar até dois professores e suas respectivas cargas horárias
    professor01, carga_hor01, professor02, carga_hor02 = extrair_professores(prof_carga_hor)

    # Retorna todos os dados coletados e processados em uma lista
    return [
        codigo_disciplina,  # Código da disciplina (ex.: "MAT1234")
        codigo_turma,       # Código da turma (ex.: "01")
        materia_turma,      # Identificador completo da matéria (ex.: "MAT123401")
        ano,                # Ano da turma (ex.: "2024")
        semestre,           # Semestre da turma (ex.: "1")
        prof_carga_hor,     # Informações brutas sobre os professores e suas cargas horárias
        professor01,        # Nome do primeiro professor (se existir)
        carga_hor01,        # Carga horária do primeiro professor
        professor02,        # Nome do segundo professor (se existir)
        carga_hor02,        # Carga horária do segundo professor
        horario,            # Horário da turma (ex.: "24T45")
        vagas_ofertadas,    # Número total de vagas ofertadas
        vagas_ocupadas,     # Número de vagas atualmente ocupadas
        local               # Local onde a turma é ministrada (ex.: "FGA - S9")
    ]

def extrair_professores(prof_carga_hor):
    """ Extrai informações sobre os professores e suas respectivas cargas horárias.
        Parâmetros:
            - prof_carga_hor: String contendo informações brutas sobre professores e cargas horárias 
            em formato como "PROFESSOR 1 (40h)<br>PROFESSOR 2 (20h)".
        Retorna:
            - Tupla com quatro valores:
            (nome do professor 1, carga horária do professor 1, nome do professor 2, carga horária do professor 2).
            Caso não existam dois professores, valores vazios ou zeros são retornados.
    """

    # Define o padrão da expressão regular para identificar os nomes dos professores e as cargas horárias.
    # Padrão:
    #       - ([A-Z\s]+): Captura um nome composto apenas de letras maiúsculas e espaços.
    #       - \((\d+h)\): Captura uma carga horária no formato "40h".
    #       - <br>: Indica separação entre os dados de professores (em HTML, "<br>" representa quebra de linha).
    #       - ?: Indica que o segundo conjunto (professor 2) é opcional.
    padrao = r"([A-Z\s]+)\((\d+h)\)\s*<br>\s*(?:([A-Z\s]+)\((\d+h)\)\s*<br>)?"

    # Remove quebras de linha desnecessárias na string e aplica a expressão regular.
    match = re.search(padrao, prof_carga_hor.replace("\n", " "))

    if match:
        # Extrai o nome do primeiro professor do primeiro grupo capturado pela regex.
        # Remove espaços em excesso.
        professor01 = match.group(1).strip()
        # Extrai a carga horária do primeiro professor do segundo grupo capturado pela regex.
        # Remove o sufixo "h" e converte para inteiro.
        carga_hor01 = int(match.group(2).strip("h"))
        # Verifica se o nome do segundo professor foi capturado (opcional).
        # Se existir, extrai o nome e remove espaços extras.
        professor02 = match.group(3).strip() if match.group(3) else ""
        # Verifica se a carga horária do segundo professor foi capturada (opcional).
        # Se existir, remove o sufixo "h" e converte para inteiro.
        carga_hor02 = int(match.group(4).strip("h")) if match.group(4) else 0

        # Retorna os dados extraídos: nomes e cargas horárias dos dois professores.
        return professor01, carga_hor01, professor02, carga_hor02

    # Caso não haja correspondência com o padrão, retorna valores padrão vazios/zeros.
    return "", 0, "", 0


def main_carregar_dados(nivel, ano, periodo):
 

    departamentos = [
        'CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA',
        'DEPTO CIÊNCIAS DA COMPUTAÇÃO - BRASÍLIA',
        'INSTITUTO DE FÍSICA - BRASÍLIA',
        'INSTITUTO DE QUÍMICA - BRASÍLIA',
        'DEPARTAMENTO DE ENGENHARIA MECANICA - BRASÍLIA',
        'DEPARTAMENTO DE MATEMÁTICA - BRASÍLIA',
    ]

    navegador = iniciar_navegador()
    dados_coletados = []

    for depto in departamentos:
        turmas = coletar_dados_turmas(navegador, nivel, depto, ano, periodo)
        dados_coletados.extend(turmas)
        print(f"Coleta do departamento '{depto}' finalizada.")
    print("=========================================================" +
          "=========================================================")
    navegador.quit()

    lista = []
    for cod_disc, cod_tur, _, _, _, _, _, _, _, _, hor, _, _, _ in dados_coletados:
        lista.append(f'{cod_disc} - Turma: {cod_tur} - Horário: {hor}')

    return lista

    # colunas = [
    #     'codigoNomeMateria', 'codigoTurma', 'materiaTurma', 'ano', 'semestre', 'profCargaHor',
    #     'professor01', 'cargahoraria01', 'professor02', 'cargahoraria02', 'horario',
    #     'vagasOfertadas', 'vagasOcupadas', 'local'
    # ]
    # arq_csv = f"./dados/csv_01_TurmasColetadasFGA_{ano}_{periodo}_{data_formatada}.csv"
    # df = pd.DataFrame(dados_coletados, columns=colunas)
    # df.to_csv(arq_csv, sep=";", encoding="utf-8", decimal=',', index=False)
    # print("Dados salvos em arquivo.")
    # print("=========================")



if __name__ == "__main__":

    data_inicio = datetime.now()
    data_formatada = data_inicio.strftime("%Y-%m-%d")


    print("===================================")
    print(f"Início: {data_inicio}")
    print("===================================")

    nivel = "GRADUAÇÃO"
    ano = "2025"
    periodo = "1"

    main_carregar_dados(nivel, ano, periodo, data_formatada)

    data_fim = datetime.now()
    print(f"Fim: {data_fim}")
    print("================================")
    print(f"Duração do processo: {data_fim - data_inicio}")
    print("====================================")

