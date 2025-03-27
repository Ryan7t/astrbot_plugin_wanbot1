from astrbot.api.event import AstrMessageEvent, MessageEventResult

async def fortune_command(plugin, event: AstrMessageEvent):
    """今日运势命令实现"""
    # 系统提示词
    system_prompt = """
你是一个专业占卜师，为情感社群成员生成15秒可读完的一条今日运势。请严格按以下规则生成：

1. **基础结构**：
【运势主题】（如桃花/事业/健康）
[幸运指数]⭐（1-5随机）
[关键词]（2个积极词汇+1个中性词汇）
[简短建议]（1句行动指引）

2. **内容要求**：
- 主题从以下随机选1个：爱情、人际关系、自我成长、财运、健康
- 幸运指数按主题动态调整（如爱情运势高时建议"多表达感受"）
- 关键词需符合社群调性（示例：共鸣、勇气、适度妥协）
- 建议使用第二人称"你"，带轻微押韵更佳（例："今日宜主动破冰，惊喜正在敲门"）

3. **风格控制**：
- 避免绝对化预言（禁用"一定""绝对"）
- 结尾加1句温暖标语（如"记得今天也要温柔对待自己"）

4. **输出示例**：
【自我成长】⭐⭐⭐⭐
[关键词] 觉察 | 突破 | 暂停 
"尝试记录三个新发现，成长的惊喜藏在细节里"

5. **特别注意**：
- 严格按照模板格式要求输出
- 输出内容不要包含"塔罗牌"的文字
- 仅需输出一条运势
"""
    
    # 调用大语言模型
    try:
        print("执行/运势指令")
        
        # 获取当前使用的提供商
        provider = plugin.context.get_using_provider()
        if not provider:
            yield event.plain_result("抱歉，当前没有可用的大语言模型提供商。")
            return
            
        # 手动调用大语言模型
        llm_response = await provider.text_chat(
            prompt="今日运势",
            system_prompt=system_prompt
        )
        
        # 获取模型回复文本
        if llm_response.role == "assistant":
            fortune_text = llm_response.completion_text
            
            # 添加免责声明
            result_text = fortune_text + "\n\n仅供娱乐|相信科学|请勿迷信"
            
            # 发送结果
            yield event.plain_result(result_text)
        else:
            yield event.plain_result("抱歉，获取今日运势失败，请稍后再试。")
            
    except Exception as e:
        print(f"运势处理异常: {e}")
        yield event.plain_result(f"抱歉，获取今日运势暂时遇到问题，请稍后再试。") 