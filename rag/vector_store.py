import os
from langchain_chroma import Chroma
from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
from model.factory import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"], # 集合名称
            embedding_function=embedding_model, # 文本嵌入模型
            persist_directory=get_abs_path(chroma_config["persist_directory"]) # 存储路径
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"]
        )

    def get_retriever(self):
        """
        把向量库变成 检索器（Retriever）
        用户提问时，自动去向量库里找最相似的内容
        :return:
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["similarity_threshold"]})

    def store_document(self):
        """
        从数据文件夹中读取数据文件，转为向量存入向量库
        :return:
        """

        def check_md5_hex(md5_for_check: str) -> str:
            """
            文件MD5去重
            :param md5_for_check: 16进制MD5字符串
            :return:
            """
            if not os.path.exists(get_abs_path(chroma_config["md5_path"])):  # 检查md5统计文件是否存在
                open(get_abs_path(chroma_config["md5_path"]), "w", encoding="utf-8").close() # 单纯创建文件
                return False
            else:
                with open(get_abs_path(chroma_config["md5_path"]), "r", encoding="utf-8") as f:
                    md5_list = [line.strip() for line in f.readlines()]
                    if md5_for_check in md5_list:
                        return True
                    else:
                        return False

        def save_md5(md5_str: str):
            """
            将传入的md5字符串保存到文件中
            :param md5_str:
            :return:
            """
            with open(get_abs_path(chroma_config["md5_path"]), 'a', encoding='utf-8') as f:
                f.write(md5_str + '\n')

        def get_file_documents(read_path: str):
            """
            加载文件
            :param read_path:
            :return: list[Document]
            """
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            elif read_path.endswith(".txt"):
                return txt_loader(read_path)
            else:
                return []

        # 返回data资源文件夹中符合格式的文件路径list
        allowed_file_path = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allowed_knowledge_file_type"])
        )

        for path in allowed_file_path:
            # 获取文件的MD5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[VectorStoreService] {path} 已存在于知识库中，跳过")
                continue
            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[VectorStoreService] {path} 无有效文本内容")
                    continue

                # 将长的 list[Document] 拆分成短的 list[Document]
                split_documents = self.spliter.split_documents(documents)

                if not split_documents:
                    logger.warning(f"[VectorStoreService] {path} 分片后无有效文本内容")
                    continue

                # 存入向量库
                self.vector_store.add_documents(split_documents)

                # 记录已经处理好的md5
                save_md5(md5_hex)

                logger.info(f"[VectorStoreService] {path} 存入向量库成功")
            except Exception as e:
                # exc_info=True 会记录详细的报错堆栈
                logger.error(f"[VectorStoreService] {path} 存入向量库失败，{str(e)}", exc_info=True)
                continue


if __name__ == '__main__':
    vs = VectorStoreService()
    vs.store_document()
    retriever = vs.get_retriever()
    response = retriever.invoke("商品全球化的作文怎么写")
    for r in response:
        print(r.page_content)
        print("-"*20)