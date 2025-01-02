from flask import Flask, render_template, request, send_file
from PIL import Image
import pytesseract
from docx import Document
import os

app = Flask(__name__)

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
        # Verifica se um arquivo foi enviado
        if "file" not in request.files:
            return "Nenhum arquivo enviado!", 400

        file = request.files["file"]

        # Verifica se o arquivo tem um nome
        if file.filename == "":
            return "Nome do arquivo inválido!", 400

        # Salva o arquivo temporariamente
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)

        # Extrai o texto da imagem
        try:
            texto = extrair_texto_da_imagem(image_path)
        except Exception as e:
            return f"Erro ao extrair texto da imagem: {e}", 500

        # Cria o arquivo Word
        word_path = os.path.join(UPLOAD_FOLDER, "output.docx")
        criar_novo_arquivo_word(word_path, texto)

        # Envia o arquivo Word para download
        return send_file(word_path, as_attachment=True)

    return render_template("index.html")

# Função para extrair texto da imagem
def extrair_texto_da_imagem(caminho_imagem):
    imagem = Image.open(caminho_imagem)
    texto = pytesseract.image_to_string(imagem, lang='por', config='--psm 6')
    return texto

# Função para criar o arquivo Word
def criar_novo_arquivo_word(caminho_saida, texto):
    doc = Document()
    for linha in texto.split("\n"):
        if linha.strip():  # Ignora linhas vazias
            doc.add_paragraph(linha)
    doc.save(caminho_saida)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')