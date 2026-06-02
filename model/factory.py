from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_deepseek import ChatDeepSeek

from langchain_core.embeddings import Embeddings
from langchain_openai.chat_models.base import BaseChatOpenAI

from utils.config_handler import rag_config
from utils.config_handler import chroma_config

class BaseModelFactory(ABC):
    """
    模型工厂抽象类（继承ABC类）
    """
    @abstractmethod
    def generator(self) -> Optional[Embeddings | ChatDeepSeek]:
        pass

class ChatModelFactory(BaseModelFactory):
    """
    Chat模型工厂类
    """
    def generator(self) -> Optional[Embeddings | ChatDeepSeek]:
        return ChatDeepSeek(model=rag_config["chat_model_name"])

class EmbeddingModelFactory(BaseModelFactory):
    """
    Embedding模型工厂类
    """
    def generator(self) -> Optional[Embeddings | ChatDeepSeek]:
        return DashScopeEmbeddings(model=rag_config["embedding_model_name"])

chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingModelFactory().generator()