import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 设置 Hugging Face 镜像源（解决国内访问问题）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 向量模型（延迟初始化）
embedding = None

def get_embedding():
    """获取 embedding 模型，首次调用时初始化"""
    global embedding
    if embedding is None:
        print("正在加载 HuggingFace 模型，请稍候...")
        embedding = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("模型加载完成！")
    return embedding
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 初始化知识库
def init_rag():
    emb = get_embedding()  # 获取 embedding 模型
    knowledge_path = os.path.join(BASE_DIR, "rag", f"english_knowledge.txt")
    # 加载文档
    loader = TextLoader(knowledge_path, encoding="utf-8")
    docs = loader.load()

    # 切分
    splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    # 存入向量库
    db = Chroma.from_documents(
        documents=splits,
        embedding=emb,
        persist_directory="./chroma_db"
    )
    return db.as_retriever(search_kwargs={"k": 2})


# 全局复用（延迟初始化）
rag_retriever = None

def get_rag_retriever():
    """获取 RAG retriever，首次调用时初始化"""
    global rag_retriever
    if rag_retriever is None:
        rag_retriever = init_rag()
    return rag_retriever


# 获取参考资料
def get_rag_context(question: str):
    try:
        retriever = get_rag_retriever()
        docs = retriever.invoke(question)
        print("参考资料-----------------", docs)
        return "\n".join([d.page_content for d in docs])
    except Exception as e:
        print(f"RAG 检索失败: {e}")
        return ""
