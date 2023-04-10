from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
import os

os.environ["OPENAI_API_KEY"] = ''
vectordb_directory = 'db'

# load the text file from disk
loader = TextLoader('My Clippings.txt')
doc = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(doc)

# initialize the embeddings
embeddings = OpenAIEmbeddings()

# check if we have a local index saved to disk
if not os.path.exists(vectordb_directory):
    # create and save the index from the docs to the disk
    print("Save the index to the disk")
    vectordb = Chroma.from_documents(docs,
                                     embeddings,
                                     persist_directory=vectordb_directory)
else:
    # load the saved index from the disk
    print("Loading the index from the disk")
    vectordb = Chroma(persist_directory=vectordb_directory,
                      embedding_function=embeddings)

# create our query
query = "what did marty cagan say about product management?"

# one final check to ensure we have an index
if not vectordb:
    print("Something is wrong, cannot load index!")
else:
    # ask the query to OpenAI with our index
    qa = RetrievalQA.from_chain_type(llm=OpenAI(model_name="text-davinci-003"),
                                     chain_type="stuff",
                                     retriever=vectordb.as_retriever())
    response = qa.run(query)
    print(response)
