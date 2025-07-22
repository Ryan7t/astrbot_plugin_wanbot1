from astrbot.api.event import AstrMessageEvent
import httpx

async def test_markdown_buttons_impl(plugin, event: AstrMessageEvent):
    '''测试发送markdown和按钮消息'''
    # 1. 检查平台类型
    platform_name = event.get_platform_name()
    if not (platform_name == "qq_official_webhook" or platform_name == "qq_official"):
        yield event.plain_result("此指令仅限在QQ官方平台使用。")
        return
    
    # 获取场景类型和相关ID
    raw_msg = getattr(event.message_obj, "raw_message", None)
    message_type = event.get_message_type()
    debug_info = ["调试信息:"]
    
    # 2. 确定场景和目标ID
    target_id = None
    message_id = None
    is_guild = False
    scene_type = "unknown"
    
    # 获取消息ID（用于被动回复）
    if hasattr(raw_msg, 'id'):
        message_id = raw_msg.id
    elif hasattr(event.message_obj, 'message_id'):
        message_id = event.message_obj.message_id
        
    debug_info.append(f"消息ID: {message_id[:5] if message_id and len(message_id) > 5 else '未获取到'}...")
    
    # 判断场景类型
    if hasattr(raw_msg, 'channel_id') or hasattr(raw_msg, 'channelId'):
        # 频道场景
        channel_id = getattr(raw_msg, 'channel_id', None) or getattr(raw_msg, 'channelId', None)
        if channel_id:
            target_id = channel_id
            is_guild = True
            scene_type = "频道"
            debug_info.append(f"场景类型: {scene_type}, 子频道ID: {target_id[:5] if target_id and len(target_id) > 5 else '未获取到'}...")
    elif event.message_obj.group_id:
        # 群聊场景
        target_id = event.message_obj.group_id
        scene_type = "群聊"
        debug_info.append(f"场景类型: {scene_type}, 群组ID: {target_id[:5] if target_id and len(target_id) > 5 else '未获取到'}...")
    else:
        # 私聊场景
        target_id = event.get_sender_id()
        scene_type = "私聊"
        debug_info.append(f"场景类型: {scene_type}, 用户ID: {target_id[:5] if target_id and len(target_id) > 5 else '未获取到'}...")
    
    if not target_id:
        yield event.plain_result("未能获取目标ID，无法发送消息。")
        return
    
    # 3. 使用已审核通过的Markdown模板
    markdown_template_id = "102283541_1745197083"
    button_template_id = "102283541_1748908035"
    
    # 4. 尝试不同的消息构造方法
    # 首先尝试被动回复方式
    try_methods = []
    
    # 方法1: 标准被动回复方式
    if message_id:
        try_methods.append({
            "method": "被动回复",
            "data": {
                "markdown": {
                    "custom_template_id": markdown_template_id
                },
                "msg_id": message_id
            }
        })
        
    # 方法2: 直接调用API，不设置msg_id（主动消息）
    try_methods.append({
        "method": "主动消息",
        "data": {
            "markdown": {
                "custom_template_id": markdown_template_id
            }
        }
    })
    
    # 方法3: 尝试msg_type=2指定为markdown类型
    if message_id:
        try_methods.append({
            "method": "带类型的被动回复",
            "data": {
                "markdown": {
                    "custom_template_id": markdown_template_id
                },
                "msg_id": message_id,
                "msg_type": 2
            }
        })
        
    # 方法4: 尝试另一种被动回复格式
    if message_id:
        try_methods.append({
            "method": "消息体内包含msg_id",
            "data": {
                "msg_id": message_id,
                "markdown": {
                    "custom_template_id": markdown_template_id
                }
            }
        })
        
    # 方法5: 使用content_type指定
    if message_id:
        try_methods.append({
            "method": "使用content_type",
            "data": {
                "msg_id": message_id,
                "content_type": 2,  # 2可能表示markdown
                "markdown": {
                    "custom_template_id": markdown_template_id
                }
            }
        })
        
    # 在频道场景下，添加按钮到所有方法
    if is_guild:
        for method in try_methods:
            method["data"]["keyboard"] = {
                "id": button_template_id
            }
            
    # 5. 获取Token
    headers = await plugin._make_headers()
    if not headers:
        err = getattr(plugin, "_last_token_error", "<未知错误>")
        yield event.plain_result(f"无法获取 QQ Bot Token，原因: {err}")
        return
        
    # 6. 依次尝试不同的方法
    success = False
    results = []
    
    # 首先发送普通文本作为回应
    yield event.plain_result(f"正在测试MD消息发送，请稍候...")
    
    for method_info in try_methods:
        method = method_info["method"]
        data = method_info["data"]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 根据场景选择API端点
                if is_guild:
                    api_url = f"https://api.sgroup.qq.com/channels/{target_id}/messages"
                elif scene_type == "群聊":
                    api_url = f"https://api.sgroup.qq.com/v2/groups/{target_id}/messages"
                else:
                    api_url = f"https://api.sgroup.qq.com/v2/users/{target_id}/messages"
                
                # 发送请求
                resp = await client.post(api_url, headers=headers, json=data)
                
                # 记录结果
                result = {
                    "method": method,
                    "status_code": resp.status_code,
                    "success": resp.status_code == 200,
                    "response": resp.text[:50] if len(resp.text) > 50 else resp.text
                }
                results.append(result)
                
                if resp.status_code == 200:
                    success = True
                    
        except Exception as e:
            results.append({
                "method": method,
                "error": str(e)[:50]
            })
            
    # 7. 报告结果
    result_text = ["测试结果:"]
    for result in results:
        if "error" in result:
            result_text.append(f"{result['method']}: 发生错误 - {result['error']}")
        else:
            status = "成功" if result["success"] else "失败"
            result_text.append(f"{result['method']}: {status} - 状态码:{result['status_code']}")
            if not result["success"]:
                result_text.append(f"  响应: {result['response']}")
                
    # 8. 只发送一条总结消息
    if success:
        result_text.append("\n有方法成功发送了MD消息!")
    else:
        result_text.append("\n所有方法都失败了。请检查机器人权限和时间限制。")
        
    # 添加调试信息
    result_text.append("\n" + "\n".join(debug_info))
    
    # 发送结果
    yield event.plain_result("\n".join(result_text))
    
    # 记录详细日志
    print(f"[测试指令] {' | '.join(debug_info)} | 结果: {success}")
    for result in results:
        if "error" in result:
            print(f"  - {result['method']}: 错误 - {result['error']}")
        else:
            print(f"  - {result['method']}: {'成功' if result['success'] else '失败'} - {result['status_code']}")
            if not result["success"]:
                print(f"    响应: {result['response']}") 