import os, hashlib
from logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def get_file_md5_hex(file_path: str):
    """
    获取文件的MD5的16进制字符串，用于文件去重
    :param file_path: 文件路径
    :return: MD5的16进制字符串
    """
    if not os.path.exists(file_path):
        logger.error(f"[MD5计算] 文件 {file_path} 不存在")
        return None

    if not os.path.isfile(file_path):
        logger.error(f"[MD5计算] {file_path} 不是一个文件")
        return None

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 文件4kb分片

    try:
        with open(file_path, "rb") as f: # 二进制打开文件
            # 分片读取文件放入hashlib.md5()对象中，以免爆内存
            while chunk := f.read(chunk_size): # 海象运算符（Walrus Operator) | 循环读取赋值
                md5_obj.update(chunk)
            return md5_obj.hexdigest()

    except Exception as e:
        logger.error(f"[MD5计算] 文件 {file_path} 读取错误 {str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """
    返回data资源文件夹中 符合格式的 文件路径list
    :return:
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] {path} 不是一个文件夹")
        return allowed_types

    for file in os.listdir(path):
        if file.endswith(allowed_types):
            files.append(os.path.join(path, file))

    return tuple(files)


def pdf_loader(file_path: str, password=None) -> list[Document]:
    """
    加载PDF文件
    :param file_path: 文件路径
    :param password: PDF文件的密码
    :return: list[Document]
    """
    return PyPDFLoader(file_path, password=password).load()

def txt_loader(file_path: str) -> list[Document]:
    """
    加载txt文件
    :param file_path: 文件路径
    :return: list[Document]
    """
    return TextLoader(file_path).load()

