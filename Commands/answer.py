from astrbot.api.event import AstrMessageEvent, MessageEventResult

async def answer_book_command(plugin, event: AstrMessageEvent):
    """答案之书命令实现"""
    # 获取用户输入的问题
    message_str = event.message_str
    # 从消息中提取问题，移除指令名称
    command_name = "答案之书"
    question = ""
    
    # 检查消息是否只包含指令名称或者有额外内容
    if message_str.strip() == command_name:
        # 如果消息只包含指令名称，则问题为空
        question = ""
    else:
        # 否则提取问题部分
        question = message_str[len(command_name):].strip()
    
    if not question:
        # 如果没有提供问题内容，提示正确的使用方式
        yield event.plain_result("请提供一个问题，例如：/答案之书 我的未来会怎样？")
        return
    
    # 默认系统提示词
    default_system_prompt = "你是一本答案之书，用户会询问你各种各样的问题，你需要像一本答案之书一样，给出一句话极其简短的话，用模棱两可或者积极向上的风格作为回答。不需要再输出其他内容"
    system_prompt = default_system_prompt
    
    # 从配置中获取提示词设置
    if hasattr(plugin, 'config') and plugin.config and 'answer_book_config' in plugin.config:
        config = plugin.config['answer_book_config']
        
        # 如果用户选择了自定义提示词
        if 'prompt_type' in config and config['prompt_type'] == '自定义':
            # 检查自定义提示词是否有效
            if 'custom_prompt' in config and config['custom_prompt'].strip():
                system_prompt = config['custom_prompt']
    
    # 调用大语言模型
    try:
        # 获取用户当前会话ID
        uid = event.unified_msg_origin
        curr_cid = await plugin.context.conversation_manager.get_curr_conversation_id(uid)
        
        # 使用 request_llm 方法调用大语言模型
        yield event.request_llm(
            prompt=question,
            system_prompt=system_prompt,
            session_id=curr_cid
        )
    except Exception as e:
        yield event.plain_result("答案之书暂时无法回答你的问题，请稍后再试。")
