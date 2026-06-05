from typing import Callable
from utils.prompt_loader import load_report_prompts, load_system_prompts
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger

@wrap_tool_call # 执行工具 前 | 后
def monitor_tool(
        # 封装模型发起的单次工具调用全量信息
        request: ToolCallRequest,
        # 函数本身
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """
    工具执行的监控
    :return:
    """
    logger.info(f"[monitor_tool] 执行工具: {request.tool_call['name']}")
    logger.info(f"[monitor_tool] 传入参数: {request.tool_call['args']}")

    try:
        # 放行：调用原始工具，拿到执行结果
        result = handler(request)
        # 后置成功日志：工具正常跑完
        logger.info(f"[monitor_tool] 工具 {request.tool_call['name']} 调用成功")

        if request.tool_call["name"] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"[monitor_tool] 模型调用工具 {request.tool_call['name']} 失败: {str(e)}")
        raise e

@before_model # 模型执行前
def log_before_model(
        state: AgentState, # 整个Agent智能体中的状态记录
        runtime: Runtime, # 记录了整个执行过程中的上下文信息
):
    """
    模型执行前输出日志
    :return:
    """
    logger.info(f"[log_before_model] 模型开始执行,带有{len(state["messages"])}条消息")
    logger.debug(f"[log_before_model] {type(state['messages'][-1].__name__)} {state["messages"][-1].content.strip()}")

@dynamic_prompt # 每一次生成提示词前调用（提示词模版）
def report_prompt_switch(request: ModelRequest):
    """
    动态切换提示词
    :return:
    """
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()
    return load_system_prompts()