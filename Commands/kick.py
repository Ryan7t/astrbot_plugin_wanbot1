from astrbot.api.event import AstrMessageEvent
from astrbot.api.message_components import At
import httpx
import re

async def kick_member_impl(plugin, event: AstrMessageEvent):
    '''踢出指令：踢出频道中的成员'''
    # 首先检查是否在频道场景中
    platform_name = event.get_platform_name()
    raw_msg = getattr(event.message_obj, "raw_message", None)
    
    # 检查是否为QQ官方频道场景
    is_guild = False
    guild_id = None
    
    # QQ官方平台的频道消息应具有guild_id或guildId属性
    if platform_name == "qq_official_webhook" or platform_name == "qq_official":
        guild_id = (getattr(raw_msg, "guild_id", None) or getattr(raw_msg, "guildId", None))
        if guild_id:
            is_guild = True
    
    # 如果不是频道场景，提示用户
    if not is_guild:
        yield event.plain_result("此指令仅限在QQ频道中使用。")
        return
    
    # 首先检查指令格式是否正确
    message_str = event.message_str
    # 如果只有/踢出，没有其他内容，直接提示正确用法
    if message_str.strip() == "/踢出":
        yield event.plain_result("请@要踢出的用户。正确用法：/踢出 原因@用户")
        return
        
    # 检查是否有@符号或<@!格式
    if '@' not in message_str and '<@!' not in message_str:
        yield event.plain_result("请@要踢出的用户。正确用法：/踢出 原因@用户")
        return
    
    # 1. 获取频道ID已在前面完成
    if not guild_id:
        yield event.plain_result("未能获取频道 ID，请在频道内使用该指令。")
        return
    
    # 2. 检查用户权限
    if event.role != "admin":
        yield event.plain_result("您没有权限执行踢出操作，需要管理员权限")
        return
    
    # 3. 获取消息中的@组件
    message_chain = event.get_messages()
    target_user_id = None
    at_component = None
    
    # 打印调试信息，查看消息链内容
    print(f"消息链内容: {message_chain}")
    
    # 使用AstrBot API获取被@的用户
    for component in message_chain:
        print(f"检查组件: {component}")
        if isinstance(component, At):
            at_component = component
            target_user_id = component.qq
            print(f"找到At组件，用户ID: {target_user_id}")
            break
    
    # 如果消息链中没有At组件，尝试从raw_message中获取
    if not target_user_id and hasattr(raw_msg, "mentions") and raw_msg.mentions:
        print(f"从raw_message.mentions中获取: {raw_msg.mentions}")
        if isinstance(raw_msg.mentions, list) and len(raw_msg.mentions) > 0:
            target_user_id = raw_msg.mentions[0]
            print(f"从mentions获取到用户ID: {target_user_id}")
    
    # 如果消息中没有@标记，检查是否有QQ官方格式的@
    if not target_user_id:
        # 检查消息中是否包含<@!数字>格式
        at_match = re.search(r'<@!(\d+)>', message_str)
        if at_match:
            target_user_id = at_match.group(1)
            print(f"从消息文本中提取到用户ID: {target_user_id}")
    
    # 如果仍未获取到目标用户，则提示正确用法
    if not target_user_id:
        yield event.plain_result("请@要踢出的用户。正确用法：/踢出 原因@用户")
        return
    
    # 4. 提取踢出原因
    message_text = message_str
    
    # 提取命令和原因
    if message_text.startswith("/踢出"):
        # 移除命令部分
        message_text = message_text[4:].strip()
        
    # 提取原因（在QQ平台中，原因和@之间没有空格）
    reason = ""
    
    # 检查QQ官方格式的@
    at_match = re.search(r'(.+?)<@!', message_text)
    if at_match:
        reason = at_match.group(1).strip()
    else:
        # 尝试匹配普通的@格式
        at_match = re.search(r'(.+?)@', message_text)
        if at_match:
            reason = at_match.group(1).strip()
    
    # 如果上面的方法都无法提取到原因，直接去掉所有@部分
    if not reason:
        # 移除QQ官方格式的@
        reason = re.sub(r'<@!\d+>', '', message_text).strip()
        # 移除普通@格式
        if at_component:
            if hasattr(at_component, 'name') and at_component.name:
                reason = reason.replace(f"@{at_component.name}", "").strip()
            reason = reason.replace(f"@{at_component.qq}", "").strip()
    
    # 如果没有原因，设置默认原因
    if not reason:
        reason = "未指定原因"
    
    # 5. 调用API踢出用户
    headers = await plugin._make_headers()
    if not headers:
        err = getattr(plugin, "_last_token_error", "<未知错误>")
        yield event.plain_result(f"无法获取 QQ Bot Token，原因: {err}")
        return
    
    payload = {
        "add_blacklist": True,  # 可以根据需求设置是否加入黑名单
        "delete_history_msg_days": 0  # 不撤回消息，可以根据需求修改
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 使用request方法发送DELETE请求，因为delete()方法不接受json参数
            resp = await client.request(
                "DELETE",
                f"https://api.sgroup.qq.com/guilds/{guild_id}/members/{target_user_id}", 
                headers=headers, 
                json=payload
            )
            
            if resp.status_code == 204:
                yield event.plain_result(f"已成功将用户踢出，原因: {reason}")
            else:
                yield event.plain_result(f"踢出用户失败，状态码 {resp.status_code}，{resp.text}")
    except Exception as e:
        yield event.plain_result(f"踢出用户时发生错误: {str(e)}") 