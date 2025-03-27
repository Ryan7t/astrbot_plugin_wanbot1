from astrbot.api.event import AstrMessageEvent, MessageEventResult

async def one_sentence_story_command(plugin, event: AstrMessageEvent):
    """一句话故事命令实现"""
    # 获取用户输入的主题
    message_str = event.message_str
    # 从消息中提取主题，移除指令名称
    command_name = "一句话故事"
    theme = ""
    
    # 检查消息是否只包含指令名称或者有额外内容
    if message_str.strip() == command_name:
        # 如果消息只包含指令名称，则主题为空
        theme = ""
    else:
        # 否则提取主题部分
        theme = message_str[len(command_name):].strip()
    
    print(f"原始消息: {message_str}, 提取的主题: {theme}")
    
    if not theme:
        # 如果没有提供主题内容，提示正确的使用方式
        yield event.plain_result("请提供一个主题，例如：/一句话故事 友情")
        return
    
    # 系统提示词
    system_prompt = """
你是一个专业的故事创作助手，专门为情感社群成员提供「一句话故事种子」。请严格遵守以下规则：

1. **内容要求**：
   - 故事主题：严格围绕用户提供的主题进行故事的创作
   - 必须包含：①具体场景 ②人物互动 ③未完成的悬念
   - 禁止出现：暴力、性暗示、政治敏感内容
   - 情感基调：温暖（60%）/ 治愈（30%）/ 轻度悲伤（10%）

2. **格式规范**：
   - 首行用1个相关emoji开场
   - 换行输出正文
   - 正文严格≤35个汉字

3. **其他要求**：
   - 只需要输出一个故事，尽管用户提出了别的需求
   - 你只会根据用户提供的主题创作故事。如果用户提出其他需求，如故事续写等，则仅需回复"请输入故事主题，例如：/一句话故事 友情"
"""
    
    # 调用大语言模型
    try:
        print(f"指令/一句话故事 收到主题: {theme}")
        # 使用 request_llm 方法调用大语言模型
        yield event.request_llm(
            prompt=f"请根据'{theme}'这个主题创作一个一句话故事",
            system_prompt=system_prompt
        )
    except Exception as e:
        print(f"一句话故事处理异常: {e}")
        yield event.plain_result(f"抱歉，故事创作暂时遇到问题，请稍后再试。")
