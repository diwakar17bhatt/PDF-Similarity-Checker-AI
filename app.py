from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

from modules.pdf_reader import extract_pdf_text
from modules.preprocess import clean_text
from modules.similarity import calculate_similarity

app = Flask(__name__)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template(
        "index.html",
        similarity=None,
        error=None
    )


@app.route("/compare", methods=["POST"])
def compare():

    try:

        if "pdf1" not in request.files or "pdf2" not in request.files:
            return render_template(
                "index.html",
                similarity=None,
                error="Please upload both PDF files."
            )

        pdf1 = request.files["pdf1"]
        pdf2 = request.files["pdf2"]

        if pdf1.filename == "" or pdf2.filename == "":
            return render_template(
                "index.html",
                similarity=None,
                error="Please select both files."
            )

        if not (
            allowed_file(pdf1.filename)
            and allowed_file(pdf2.filename)
        ):
            return render_template(
                "index.html",
                similarity=None,
                error="Only PDF files are allowed."
            )

        filename1 = secure_filename(pdf1.filename)
        filename2 = secure_filename(pdf2.filename)

        path1 = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename1
        )

        path2 = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename2
        )

        pdf1.save(path1)
        pdf2.save(path2)

        text1 = extract_pdf_text(path1)
        text2 = extract_pdf_text(path2)

        if not text1.strip():
            return render_template(
                "index.html",
                similarity=None,
                error=f"No readable text found in {filename1}"
            )

        if not text2.strip():
            return render_template(
                "index.html",
                similarity=None,
                error=f"No readable text found in {filename2}"
            )

        clean_text1 = clean_text(text1)
        clean_text2 = clean_text(text2)

        similarity = calculate_similarity(
            clean_text1,
            clean_text2
        )

        return render_template(
            "index.html",
            similarity=similarity,
            file1=filename1,
            file2=filename2,
            error=None
        )

    except Exception as e:

        return render_template(
            "index.html",
            similarity=None,
            error=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
