from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

from modules.pdf_reader import extract_pdf_text
from modules.preprocess import clean_text
from modules.similarity import calculate_similarity

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Check file extension
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Home Page
@app.route("/")
def home():
    return render_template(
        "index.html",
        similarity=None,
        error=None
    )


# Compare PDFs
@app.route("/compare", methods=["POST"])
def compare():

    try:

        # Check uploads
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

        # Secure filenames
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

        # Save files
        pdf1.save(path1)
        pdf2.save(path2)

        # Extract text
        text1 = extract_pdf_text(path1)
        text2 = extract_pdf_text(path2)

        # Check extraction
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

        # NLP preprocessing
        clean_text1 = clean_text(text1)
        clean_text2 = clean_text(text2)

        # Similarity
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


# Run App
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )