import os
import warnings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, Docx2txtLoader

# 忽略 ChromaDB 的遥测警告
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")

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
    try:
        emb = get_embedding()  # 获取 embedding 模型
        
        # 加载所有知识库文档
        all_docs = []
        
        # 1. 加载英文知识文本文件
        knowledge_path = os.path.join(BASE_DIR, "rag", "english_knowledge.txt")
        if os.path.exists(knowledge_path):
            loader = TextLoader(knowledge_path, encoding="utf-8")
            docs = loader.load()
            all_docs.extend(docs)
            print(f"已加载 english_knowledge.txt: {len(docs)} 个文档")
        else:
            print(f"警告: 知识库文件不存在: {knowledge_path}")
        
        # 2. 加载新概念英语 Word 文档
        new_concept_path = os.path.join(BASE_DIR, "rag", "new_concept.docx")
        if os.path.exists(new_concept_path):
            loader = Docx2txtLoader(new_concept_path)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"已加载 new_concept.docx: {len(docs)} 个文档")
        else:
            print(f"警告: 知识库文件不存在: {new_concept_path}")
        
        # 检查是否有文档被加载
        if not all_docs:
            print("警告: 没有加载任何知识库文档")
            return None
        
        # 切分文档
        splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        splits = splitter.split_documents(all_docs)

        # 存入向量库（首次创建，不使用旧的序列化数据）
        db = Chroma.from_documents(
            documents=splits,
            embedding=emb,
            persist_directory="./chroma_db"
        )
        print(f"RAG 知识库初始化成功，共 {len(splits)} 个文档块")
        return db.as_retriever(search_kwargs={"k": 2})
    except Exception as e:
        print(f"RAG 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None


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
        if retriever is None:
            print("RAG retriever 未初始化，跳过检索")
            return ""
        
        docs = retriever.invoke(question)
        if docs:
            print(f"RAG 检索成功，找到 {len(docs)} 个相关文档")
            return "\n".join([d.page_content for d in docs])
        else:
            print("RAG 未找到相关文档")
            return ""
    except Exception as e:
        print(f"RAG 检索失败: {e}")
        import traceback
        traceback.print_exc()
        return ""
