"""AI Career Intelligence Flask application."""
import os

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from utils.pdf_utils import extract_text_from_pdf

app = Flask(__name__)

# Secret key for Flask flash messages
app.secret_key = "career-intelligence-secret-key"

# Folder for uploaded resumes
UPLOAD_FOLDER = "uploads"

# Maximum upload size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

@app.errorhandler(413)
def file_too_large(_error):
    """Handle files that exceed the maximum upload size."""
    flash("File is too large. Maximum allowed size is 5 MB.")
    return redirect(url_for("home"))

# Only PDF files are allowed
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    """Check whether the uploaded file has a PDF extension."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    """Display the home page."""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle resume upload, validation, and PDF text extraction."""

    # Check whether a file was submitted
    if "resume" not in request.files:
        flash("Please select a resume PDF before submitting.")
        return redirect(url_for("home"))

    file = request.files["resume"]

    # Check whether the user selected a file
    if file.filename == "":
        flash("No file selected. Please choose a PDF resume.")
        return redirect(url_for("home"))

    # Check whether the file is a PDF
    if not allowed_file(file.filename):
        flash("Invalid file type. Only PDF files are allowed.")
        return redirect(url_for("home"))

    # Make sure the uploads folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Make the filename safe
    filename = secure_filename(file.filename)

    # Create the complete file path
    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    # Save the uploaded PDF
    file.save(file_path)

    # Extract text from the PDF
    try:
        resume_text = extract_text_from_pdf(file_path)

        print("\n========== EXTRACTED RESUME TEXT ==========\n")
        print(resume_text)
        print("\n============================================\n")

        # Check whether any text was extracted
        if not resume_text.strip():
            flash("The PDF was uploaded, but no readable text was found.")
            return redirect(url_for("home"))

        # Display extracted text on the preview page
        return render_template(
            "preview.html",
            resume_text=resume_text
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        print("PDF extraction error:", e)
        flash("The PDF was uploaded, but text extraction failed.")
        return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)
