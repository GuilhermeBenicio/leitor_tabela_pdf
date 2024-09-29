import PySimpleGUI as sg
import pdfplumber
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("ARQUIVO JSON AQUI")
firebase_admin.initialize_app(cred)
db = firestore.client()

def processar_pdf(arquivo):
    dados_extraidos = []
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            tabela = pagina.extract_table()
            if tabela:
                linha_especifica = 1
                coluna_especifica = 0
                if linha_especifica < len(tabela):
                    dado = tabela[linha_especifica][coluna_especifica]
                    dados_extraidos.append(dado)
                else:
                    return "Linha especificada não existe."
    return dados_extraidos if dados_extraidos else "Nenhuma tabela encontrada"

def inserir_dados_firebase(colecao, dados):
    try:
        for dado in dados:
            db.collection(colecao).add({'nome': dado})
        return "Dados inseridos com sucesso no Firestore."
    except Exception as e:
        return str(e)

layout_login = [
    [sg.Text("Nome da Coleção Firebase:"), sg.Input(key='-COLLECTION-')],
    [sg.Button("Confirmar"), sg.Button("Sair")]
]

window_login = sg.Window("Conectar ao Firestore", layout_login)

while True:
    event, values = window_login.read()
    if event == sg.WINDOW_CLOSED or event == "Sair":
        window_login.close()
        exit()
    if event == "Confirmar":
        colecao = values['-COLLECTION-']
        if colecao:
            window_login.close()
            break
        else:
            sg.popup("Por favor, insira o nome da coleção.")

layout = [
    [sg.Text("Selecione um arquivo PDF:")],
    [sg.Input(), sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
    [sg.Button("Processar"), sg.Button("Sair")],
    [sg.Multiline(size=(50, 10), key='-RESULTADO-', disabled=True)]
]

window = sg.Window("Leitor de PDF", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Sair":
        break
    if event == "Processar":
        arquivo_pdf = values[0]
        if arquivo_pdf:
            dados_extraidos = processar_pdf(arquivo_pdf)
            if isinstance(dados_extraidos, list):
                resultado = inserir_dados_firebase(colecao, dados_extraidos)
                window['-RESULTADO-'].update(resultado)
            else:
                window['-RESULTADO-'].update(dados_extraidos)
        else:
            sg.popup("Por favor, selecione um arquivo PDF.")

window.close()
