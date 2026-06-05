import os
from utils.logger_handler import logger
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]

external_data = {}

@tool(description="从向量库中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"{city}天气为晴天，气温26摄氏度，空气适度50%，南风一级，AQI21，最近6小时降雨概率极低。"

@tool(description="获取用户所在城市名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["杭州", "苏州", "上海"])

@tool(description="获取用户ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)

@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    return "9"

def generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"[generate_external_data] {external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]: # 跳过第一行标题
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('""', "")
                feature: str = arr[1].replace('""', "")
                efficiency: str = arr[2].replace('""', "")
                consumables: str = arr[3].replace('""', "")
                comparison: str = arr[4].replace('""', "")
                time: str = arr[5].replace('""', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "消耗": consumables,
                    "对比": comparison,
                }



@tool(description="从外部系统中获取用户的使用记录，以纯字符串形式返回，如未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data] 未找到用户{user_id}的{month}月数据")
        return ""

