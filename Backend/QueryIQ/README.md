# 🤖 QueryIQ: Customer Query Retrieval-Augmented Generation (RAG)

## Demonstration
Integrating LLM (Llama-3) to perform Retrieval-Augmented Generation (RAG) providing instant, relevant, personalized and accurate user queries and real-time support.

Whether you run a local hair styling business or a Michelin Star restaurant like Aretti, this application is design to revolutionzie customer service for your business


## Why RAG Matters?
Customers need responses that are RELEVANT and SPECIFIC to the business. That is where RAG comes in. It performs two critical functions: Retrieval and Generation. 

### RETREIVAL: 
Businesses can input files and documents specific to their operations (e.g, product manuals, FAQs, policies) into QueryIQ. RAG searches a document database to identify relevant chunks of data. QueryIQ then uses vector embeddings stored in ChromaDB to compare semantic similarity of the query. This helps the application learn information that is specific and accurate to the business.

### GENERATION:
Once the relevant documents are retrieved, QueryIQ integrates a local, containerized large language model (LLM) generates a response. This allows the application to form coherent responses relevant to the data it receives and are generated instantly, providing real-time support to customers 

## WORKFLOW:
1. Query -> Tokenization -> Embedding -> Dense Vector Representation
2. Query Vector => Searching for embeddings stored in ChromaDB using cosine similarity  = FOUND
3. Retrieved chunks of information -> Llama-3 Prompting -> Response 
4. Output validation -> Response truncation -> Response in Text


## 🛠 Technologies and Frameworks Used
1. Python
2. ChromaDB - Vector Database
3. Ollama API
4. LangChain Library



## 🚀 Getting Started
Ensure you have Ollama, specifically the Llama-3 model installed
1. ```bash
   git clone https://github.com/Shirly8/queryiq.git
   cd queryiq


3.  ```bash
    install [dependencies]
    python Query.py --query "ENTER QUERY HERE'

