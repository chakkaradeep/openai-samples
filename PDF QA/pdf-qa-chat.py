import configparser
import json
import os
import re
import sys
from typing import Optional

import pdfplumber
from langchain import OpenAI, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


def preprocess(text):
    """
    This function preprocesses the input text by replacing newlines with spaces and removing consecutive whitespaces
    using regex.
    :param text:
    :return: text
    """
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text


def extract_page_text(file_path: str, start_page: Optional[int] = 0, num_pages: Optional[int] = 3) -> str:
    """
    This function takes a PDF file path and extracts text from the specified page range.
    It takes three parameters:
    :param file_path:a string representing the file path of the PDF file
    :param start_page:an optional integer representing the starting page number to extract text from. The default value is 0.
    :param num_pages:an optional integer representing the number of pages to extract text from. The default value is 3.
    :return:pdf text
    """
    with pdfplumber.open(file_path) as pdf:
        pages_text = []
        for page_number in range(start_page, start_page + num_pages):
            if page_number < len(pdf.pages):
                page = pdf.pages[page_number]
                text = preprocess(page.extract_text())
                pages_text.append(text)
        combined_text = ' '.join(pages_text)
    return combined_text


def generate_pdf_summary_chain(text: str, chain: BaseCombineDocumentsChain) -> str:
    """
    This function takes in a string of text and a summary chain object and generates a summary of the
    text using the specified chain. The text is split using a RecursiveCharacterTextSplitter, then documents are
    created from the resulting text segments. The chain is then applied to the documents to generate the summary.
    :param text:pdf text
    :param chain:summary chain
    :return:concise summary of the text
    """
    text_splitter = RecursiveCharacterTextSplitter()
    texts = text_splitter.split_text(text)
    docs = text_splitter.create_documents(texts=texts)
    summary = chain.run(docs)
    return summary


def generate_pdf_summary(source_path: str = "papers", output_file: str = "summaries.json"):
    """
    This function takes in a folder path and generates summaries of all the PDF files in that folder.
    The summaries are stored in an output file for later retrieval. If the output file already exists, the
    function loads and displays the existing summaries; otherwise, it generates new summaries for each
    PDF file and stores them in the output file. The summary is generated using OpenAI's GPT-3 model
    which is fed with a prompt template and the text extracted from the first page of each PDF.
    The generated summaries are displayed and also saved to the output file as a JSON array of file names
    and their corresponding summaries.
    :param source_path: Path to the folder containing PDF files. Default value is 'papers'
    :param output_file: Name of the output file to store the summaries. Default value is 'summaries.json'
    """
    summaries = []

    prompt_template = """
                        Write a concise summary of the following in passive voice no more than 150 words.\n
                        Example of a passive voice sentence: The package was delivered by the courier to the recipient's address.\n
                        Include key details such as the main findings and implications of the text.\n

                        {text}\n

                        Example response:\n
                        A pipeline was proposed to generate a high-quality multi-turn chat corpus using ChatGPT to converse with itself. The resulting Baize model demonstrated good performance in multi-turn dialogues with guardrails that minimize potential risks. Baize model and data were released for research purposes only."""
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    summary_chain = load_summarize_chain(OpenAI(temperature=0, max_tokens=300),
                                         chain_type="stuff",
                                         prompt=prompt)

    if os.path.exists(output_file):
        print("\nLoading PDF summaries...\n")
        with open(output_file, "r") as infile:
            summaries = json.load(infile)
            for summary in summaries:
                print("\033[93m" + f"{summary['file_name']} Summary:" + "\033[0m")
                print(f"{summary['summary']}\n")
    else:
        print("\nGenerating PDF summaries...\n")
        summaries = []
        for file_name in os.listdir(source_path):
            if file_name.lower().endswith(".pdf"):
                file_path = os.path.join(source_path, file_name)
                first_page_text = extract_page_text(file_path)
                summary = generate_pdf_summary_chain(first_page_text, summary_chain)

                summary_data = {
                    "file_name": file_name,
                    "summary": summary.strip()
                }
                summaries.append(summary_data)

                print("\033[93m" + f"{file_name} Summary:" + "\033[0m")
                print(f"{summary}\n")

        # Save the summaries to the JSON file
        with open(output_file, "w") as outfile:
            json.dump(summaries, outfile, indent=2)


def create_vectordb(vectordb_dir_path: str = "chroma_db"):
    """
    Creates a vector database for the PDF files in the 'papers' directory, using the Chroma library.

    This function iterates through each PDF file in the directory, splits its text into smaller chunks, creates Document
    instances from the text chunks, and extracts document embeddings using OpenAI's GPT-3 model. Then it uses Chroma to
    store the embeddings in a vector database on disk.

    :param vectordb_dir_path: The path to the directory where the vector database should be stored. If the directory
                              does not exist, it will be created. Default value is 'chroma_db'.
    """
    if not os.path.exists(vectordb_dir_path):
        embeddings = OpenAIEmbeddings()

        for file_name in os.listdir("papers"):
            if file_name.lower().endswith('.pdf'):
                file_path = os.path.join("papers", file_name)
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000
                )
                pdf = UnstructuredPDFLoader(file_path, strategy="fast")
                docs = pdf.load_and_split(text_splitter=text_splitter)
                Chroma.from_documents(docs,
                                      embeddings,
                                      persist_directory=vectordb_dir_path)


def load_vectordb(vectordb_dir_path: str = "chroma_db") -> Chroma:
    """
    Load a Chroma vector database from the specified directory.

    :param vectordb_dir_path: Directory path where the Chroma object is stored.
    :return: A Chroma object loaded from the specified directory.
    """
    if not os.path.exists(vectordb_dir_path):
        raise FileNotFoundError("Vector database not found. Create them first.")
    else:
        embeddings = OpenAIEmbeddings()
        vectordb = Chroma(persist_directory=vectordb_dir_path,
                          embedding_function=embeddings)
        return vectordb


def generate_pdf_embeddings(vectordb_dir_path: str = "chromadb") -> Chroma:
    """
    This function generates Chroma vector database for PDF documents in the specified directory to store
    OpenAI embeddings. If the Chroma database does not exist, it will be created first.
    :param vectordb_dir_path: directory path for the Chroma database. Default value is 'chromadb'
    :return: Chroma object with the PDF embeddings
    """
    if not os.path.exists(vectordb_dir_path):
        create_vectordb()
    return load_vectordb()


def query_dataset_retrieval(query: str, qa_chain: BaseRetrievalQA):
    """
    Execute the RetrievalQA chain
    :param query: Query to execute
    :param qa_chain: The RetrievalQA chain object
    """
    response = qa_chain.run(query)
    return response


def process_input(user_input: str, vectordb: Chroma):
    """
    Get input from the user and perform a Retrieval QA on the PDF documents which are stored as embeddings.
    :param user_input: Input text from the user
    :param vectordb: Chroma vector database
    """
    prompt_template = """
        Use the following pieces of context to answer the question at the end.\n 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.\n

        {context}\n

        Question: {question}\n
        Answer:"""
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": prompt}
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    qa_chain = RetrievalQA.from_chain_type(OpenAI(temperature=0, max_tokens=400),
                                           chain_type="stuff",
                                           retriever=retriever,
                                           chain_type_kwargs=chain_type_kwargs)

    sys.stdout.write(".....waiting for magic.....")
    sys.stdout.flush()
    try:
        response = query_dataset_retrieval(user_input, qa_chain)
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        print(response, "\n")
        return None
    except Exception as e:
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        error_message = f"AI Assistant encountered an error. Please try again later.\nError:{e} "
        print(error_message)
        return error_message


def get_user_input(vectordb: Chroma):
    """
    Get user input and process it
    :param vectordb: Chroma vector database
    """
    while True:
        user_input = input(f"\nYour question: ")
        if user_input.lower() == 'exit':
            break
        else:
            error_message = process_input(user_input, vectordb)
            if error_message is not None:
                break


def main():
    """
    Our main function
    """
    generate_pdf_summary()
    vectordb = generate_pdf_embeddings()
    get_user_input(vectordb)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    os.environ["OPENAI_API_KEY"] = config.get('API_KEYS', 'OPENAI_API_KEY')

    main()
