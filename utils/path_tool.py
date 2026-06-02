"""
为整个工程提供统一的绝对路径
"""
import os

def get_project_root() -> str:
    """
    获取工程根目录
    :return: 根目录字符串
    """
    # 获取当前文件的绝对路径
    current_file = os.path.abspath(__file__)
    # 获取文件的文件夹路径
    parent_dir = os.path.dirname(current_file)
    # 获取项目的根目录
    project_root = os.path.dirname(parent_dir)

    return project_root

def get_abs_path(relative_path: str) -> str:
    """
    获取绝对路径
    :param relative_path: 相对路径
    :return: 绝对路径
    """
    project_root = get_project_root()
    abs_path = os.path.join(project_root, relative_path)

    return abs_path



if __name__ == '__main__':
    print(get_project_root())
    print(get_abs_path('data/md5.txt'))