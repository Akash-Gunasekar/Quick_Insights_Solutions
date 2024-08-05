from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from neo4j import GraphDatabase

app = Flask(__name__)
CORS(app)

# Set up Hugging Face token
HF_token = "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"  # Replace with your token or ensure it's set in the environment

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "Password@24"

# Global variables for embeddings, vectorstore, and QA chain
embeddings = None
vectorstore = None
qa = None

def fetch_data_from_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    with driver.session() as session:
        result = session.run(query)
        data = []
        for record in result:
            node = record["n"]
            relationship = record["r"]
            related_node = record["m"]
            data.append(f"Node: {node}, Relationship: {relationship}, Related Node: {related_node}")
    driver.close()
    return "\n".join(data)

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

@app.route('/questionanswering', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    prompt = f"{query}"

    try:
        # Use the QA chain to generate a response
        response = qa.invoke(prompt)
        full_response = response['result']

        # Find the position of "Helpful Answer:"
        start_pos = full_response.find("Helpful Answer:")
        if start_pos != -1:
            # Extract the part after "Helpful Answer:"
            helpful_answer = full_response[start_pos + len("Helpful Answer:"):].strip()
        else:
            helpful_answer = full_response.strip()
        
        return jsonify({"response": helpful_answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Fetch data from Neo4j and initialize resources
    neo4j_text = fetch_data_from_neo4j(uri, user, password)
    initialize_resources(neo4j_text)

    app.run(debug=True, port=5001)
