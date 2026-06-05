from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.documents import Document

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt

class RagSummarizeService(object):
    """
    总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型回复
    """
    def __init__(self):
        self.vector_store = VectorStoreService() # RAG 向量库存储服务
        self.retriever = self.vector_store.get_retriever() # RAG 检索器
        self.prompt_text = load_rag_prompts() # RAG 提示词
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) # RAG 提示词模版
        self.model = chat_model
        self.chain = self.init_chain()

    def init_chain(self):
        return self.prompt_template | print_prompt | self.model | StrOutputParser()

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:

        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]: 内容: {doc.page_content} | 参考元数据: {doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context
            }
        )

if __name__ == '__main__':
    rag_service = RagSummarizeService()
    rag_service.vector_store.store_document()
    print(rag_service.rag_summarize("小户型适合哪些扫地机器人"))