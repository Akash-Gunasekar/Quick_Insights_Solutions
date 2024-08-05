from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
from docx import Document
from flask_cors import CORS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA

app = Flask(__name__)
CORS(app)

# Set up Hugging Face token
HF_token = "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"  # Replace with your token or ensure it's set in the environment

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for embeddings, vectorstore, and QA chain
embeddings = None
vectorstore = None
qa = None

def initialize_resources(content):
    global embeddings, vectorstore, qa

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1028, chunk_overlap=0)
    chunking = text_splitter.split_text(content)

    # Initialize embeddings
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=HF_token,
        model_name="pinecone/bert-retriever-squad2"
    )

    # Initialize vectorstore
    vectorstore = Chroma.from_texts(chunking, embeddings)

    # Initialize the Hugging Face model
    model = HuggingFaceHub(repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                           model_kwargs={"temperature": 0.5, "max_new_tokens": 512, "max_length": 64},
                           huggingfacehub_api_token=HF_token)

    # Initialize retriever and QA chain
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 1})
    qa = RetrievalQA.from_chain_type(llm=model, retriever=retriever, chain_type="stuff")

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/docxinsights', methods=['POST'])
def process_request():
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['document']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if 'query' not in request.form:
            return jsonify({"error": "No query part"}), 400
        customer_query = request.form['query']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Determine the file type and extract text accordingly
            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.docx'):
                content = extract_text_from_docx(filepath)
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filename.lower().endswith('.doc'):
                return jsonify({"error": "DOC format not supported. Please convert to DOCX."}), 400
            else:
                return jsonify({"error": "Unsupported file format"}), 400

            # Initialize resources with the extracted text content
            initialize_resources(content)

            # Use the QA chain to generate a response
            response = qa.invoke(customer_query)
            full_response = response['result']

            # Extract part of the response after "Helpful Answer"
            helpful_answer = full_response.split("Helpful Answer:")[-1].strip()  # Gets text after "Helpful Answer"

            # Return the response
            return jsonify({"message": "File uploaded and processed successfully", "filename": filename, "response": helpful_answer}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
