from flask import Flask, render_template, request, send_file
from PIL import Image
import pytesseract
import os

app = Flask(__name__)

# Configura a variável de ambiente para o Tesseract
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'

# Configura o caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Pasta temporária para armazenar arquivos
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Verifica se os arquivos foram enviados
        if "files" not in request.files:
            return "Nenhum arquivo enviado!", 400

        files = request.files.getlist("files")

        # Verifica se pelo menos um arquivo foi enviado
        if not files or all(file.filename == "" for file in files):
            return "Nenhum arquivo válido enviado!", 400

        texto_total = ""

        # Processa cada arquivo
        for file in files:
            # Salva o arquivo temporariamente
            image_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image_path)

            # Extrai o texto da imagem
            try:
                texto = extrair_texto_da_imagem(image_path)
                texto_total += texto + "\n"  # Adiciona o texto ao total
            except Exception as e:
                return f"Erro ao extrair texto da imagem {file.filename}: {e}", 500

        # Cria o arquivo TXT
        txt_path = os.path.join(UPLOAD_FOLDER, "output.txt")
        criar_novo_arquivo_txt(txt_path, texto_total)

        # Envia o arquivo TXT para download
        return send_file(txt_path, as_attachment=True)

    return render_template("index.html")

# Função para extrair texto da imagem e colocar em uma única linha com quebras no ponto final
def extrair_texto_da_imagem(caminho_imagem):
    imagem = Image.open(caminho_imagem)
    # Usa o image_to_string para extrair o texto
    texto = pytesseract.image_to_string(imagem, lang='por', config='--psm 6')

    # Concatena o texto em uma única linha, adicionando quebras no ponto final
    texto_formatado = ""
    for linha in texto.split("\n"):
        texto_formatado += linha.strip() + " "

    # Substitui pontos finais por ponto final + quebra de linha
    texto_formatado = texto_formatado.replace(". ", ".\n")

    return texto_formatado.strip()

# Função para criar o arquivo TXT
def criar_novo_arquivo_txt(caminho_saida, texto):
    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')