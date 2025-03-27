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
    
    if not theme:
        # 如果没有提供主题内容，提示正确的使用方式
        yield event.plain_result("请提供一个主题，例如：/一句话故事 友情")
        return
    
    # 默认系统提示词
    default_system_prompt = """
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
    system_prompt = default_system_prompt
    
    # 从配置中获取提示词设置
    if hasattr(plugin, 'config') and plugin.config and 'story_config' in plugin.config:
        config = plugin.config['story_config']
        
        # 如果用户选择了自定义提示词
        if 'prompt_type' in config and config['prompt_type'] == '自定义':
            # 检查自定义提示词是否有效
            if 'custom_prompt' in config and config['custom_prompt'].strip():
                system_prompt = config['custom_prompt']
    
    # 调用大语言模型
    try:
        # 使用 request_llm 方法调用大语言模型
        yield event.request_llm(
            prompt=theme,
            system_prompt=system_prompt
        )
    except Exception as e:
        yield event.plain_result("抱歉，故事创作暂时遇到问题，请稍后再试。")
