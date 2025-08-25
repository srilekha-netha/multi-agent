import os
import streamlit as st
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.retrievers import BM25Retriever

# Correct Groq import
from langchain_groq import ChatGroq

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

# ----------------------------
# LLM Setup (Groq)
# ----------------------------
def get_llm(model: str = "llama3-8b-8192", temperature: float = 0.2):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Missing GROQ_API_KEY. Please set it in your `.env` file.")
        st.stop()

    return ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=api_key  # correct kwarg for ChatGroq
    )

# ----------------------------
# Load & Chunk Documents
# ----------------------------
def load_and_chunk(file_path: str):
    if not file_path or not os.path.exists(file_path):
        return []

    loader = Docx2txtLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    return chunks

# ----------------------------
# Build Retrievers
# ----------------------------
def build_retrievers(docs):
    salary_chunks = docs.get("salary", [])
    insurance_chunks = docs.get("insurance", [])

    bm25_salary = BM25Retriever.from_documents(salary_chunks) if salary_chunks else None
    bm25_insurance = BM25Retriever.from_documents(insurance_chunks) if insurance_chunks else None

    return {"salary": bm25_salary, "insurance": bm25_insurance}

# ----------------------------
# Agents
# ----------------------------
def salary_agent(query: str, retriever, llm) -> str:
    if not retriever:
        return "No salary data available."

    salary_docs = retriever.get_relevant_documents(query)
    context = "\n".join([d.page_content for d in salary_docs])

    prompt = f"""
    You are the **Salary Agent**. Use the following context to answer.

    Context:
    {context}

    Question: {query}

    Answer clearly about salary details:
    """
    return "🧑‍💼 Salary Agent: " + llm.invoke(prompt).content

def insurance_agent(query: str, retriever, llm) -> str:
    if not retriever:
        return "No insurance data available."

    insurance_docs = retriever.get_relevant_documents(query)
    context = "\n".join([d.page_content for d in insurance_docs])

    prompt = f"""
    You are the **Insurance Agent**. Use the following context to answer.

    Context:
    {context}

    Question: {query}

    Answer clearly about insurance details:
    """
    return "🏥 Insurance Agent: " + llm.invoke(prompt).content

def coordinator_agent(query: str, salary_ans: str, insurance_ans: str, llm) -> str:
    prompt = f"""
    You are the **Coordinator Agent**. Combine the following answers into one clear response.

    Salary Agent Answer:
    {salary_ans}

    Insurance Agent Answer:
    {insurance_ans}

    User Question: {query}

    Provide a helpful, concise final answer for the user.
    """
    return "🤝 Coordinator Agent: " + llm.invoke(prompt).content

# ----------------------------
# Manage Documents in Sidebar
# ----------------------------
def manage_documents():
    st.sidebar.header("📂 Documents")
    os.makedirs("data", exist_ok=True)

    salary_file = "data/salary.docx"
    insurance_file = "data/insurance.docx"

    # --- Salary Document Section ---
    st.sidebar.subheader("🧑‍💼 Salary Document")
    if os.path.exists(salary_file):
        st.sidebar.success(f"✅ {salary_file}")
        if st.sidebar.button("🗑️ Delete Salary Document"):
            os.remove(salary_file)
            st.sidebar.warning("Deleted Salary Document. Please upload again.")
    else:
        st.sidebar.info("No Salary document uploaded yet.")

    uploaded_salary = st.sidebar.file_uploader("Upload Salary DOCX", type=["docx"], key="salary")
    if uploaded_salary:
        with open(salary_file, "wb") as f:
            f.write(uploaded_salary.read())
        st.sidebar.success("✅ Salary document uploaded!")

    # --- Insurance Document Section ---
    st.sidebar.subheader("🏥 Insurance Document")
    if os.path.exists(insurance_file):
        st.sidebar.success(f"✅ {insurance_file}")
        if st.sidebar.button("🗑️ Delete Insurance Document"):
            os.remove(insurance_file)
            st.sidebar.warning("Deleted Insurance Document. Please upload again.")
    else:
        st.sidebar.info("No Insurance document uploaded yet.")

    uploaded_insurance = st.sidebar.file_uploader("Upload Insurance DOCX", type=["docx"], key="insurance")
    if uploaded_insurance:
        with open(insurance_file, "wb") as f:
            f.write(uploaded_insurance.read())
        st.sidebar.success("✅ Insurance document uploaded!")

    return salary_file if os.path.exists(salary_file) else None, insurance_file if os.path.exists(insurance_file) else None

# ----------------------------
# Streamlit UI
# ----------------------------
def main():
    st.set_page_config(page_title="Multi-Agent", layout="wide")
    st.title("🤖 Multi-Agent")

    # Manage documents in sidebar
    salary_file, insurance_file = manage_documents()

    # Load docs safely
    docs = {
        "salary": load_and_chunk(salary_file),
        "insurance": load_and_chunk(insurance_file)
    }

    # Build retrievers
    stores = build_retrievers(docs)

    # Initialize LLM
    llm = get_llm()

    # User Input
    query = st.text_input("Ask a question (about salary or insurance):")

    if query:
        with st.spinner("🤔 Agents are working..."):
            query_lower = query.lower()
            salary_ans, insurance_ans, final_ans = None, None, None

            # Salary-only
            if "salary" in query_lower and "insurance" not in query_lower:
                salary_ans = salary_agent(query, stores.get("salary"), llm)
                st.subheader("🧑‍💼 Salary Agent Answer")
                st.write(salary_ans)

            # Insurance-only
            elif "insurance" in query_lower and "salary" not in query_lower:
                insurance_ans = insurance_agent(query, stores.get("insurance"), llm)
                st.subheader("🏥 Insurance Agent Answer")
                st.write(insurance_ans)

            # Both Salary + Insurance → Coordinator
            elif "salary" in query_lower and "insurance" in query_lower:
                salary_ans = salary_agent(query, stores.get("salary"), llm)
                insurance_ans = insurance_agent(query, stores.get("insurance"), llm)
                final_ans = coordinator_agent(query, salary_ans, insurance_ans, llm)

                st.subheader("🧑‍💼 Salary Agent Answer")
                st.write(salary_ans)
                st.subheader("🏥 Insurance Agent Answer")
                st.write(insurance_ans)
                st.subheader("🤝 Coordinator Agent Final Answer")
                st.success(final_ans)

            # If neither keyword found
            else:
                st.warning("⚠️ Please ask about **salary** or **insurance**.")

if __name__ == "__main__":
    main()
