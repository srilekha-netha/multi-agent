# 🤖 Multi-Agent RAG Chatbot

This project is a **Streamlit-based Multi-Agent Chatbot** powered by **LangChain + Groq LLM**.  
It allows users to upload **Salary** and **Insurance** documents (`.docx`), and then query them interactively.  
The chatbot uses **BM25 Retriever** for document search and different **agents** to provide domain-specific answers.  

---

## Features
- 📂 **Document Management**  
  - Upload Salary and Insurance `.docx` files directly from the sidebar.  
  - View which documents are currently loaded.  
  - Delete existing files and upload new ones.  

- 🤖 **Multi-Agent Workflow**  
  - **Salary Agent** → Answers salary-related queries.  
  - **Insurance Agent** → Answers insurance-related queries.  
  - **Coordinator Agent** → Combines both responses into a final, concise answer if the query involves both.  

- 🔍 **Retrieval-Augmented Generation (RAG)**  
  - Uses **BM25 Retriever** for semantic document search.  
  - Splits documents into smaller chunks for more accurate retrieval.  

- ⚡ **Groq LLM Integration**  
  - Powered by **Groq API (LLaMA3-8B-8192)** for fast and efficient reasoning. 
