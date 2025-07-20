from astrbot.api.event import AstrMessageEvent
import httpx

async def get_guild_details_impl(plugin, event: AstrMessageEvent):
    '''频道管理：获取频道详细信息实现'''  
    raw_msg = getattr(event.message_obj, "raw_message", None)
    api_guild_id = (getattr(raw_msg, "guild_id", None)
                    or getattr(raw_msg, "guildId", None)
                    or event.get_group_id()
                    or event.get_session_id())
    if not api_guild_id:
        yield event.plain_result("未能获取频道 ID，请在频道/群组内使用该指令。")
        return
    prefix = (
        f"当前框架获取的群组id: {api_guild_id}\n"
        f"官方原始 guild_id: {getattr(raw_msg, 'guild_id', None) or getattr(raw_msg, 'guildId', None)}\n"
        f"官方 channel_id: {getattr(raw_msg, 'channel_id', None) or getattr(raw_msg, 'channelId', None)}\n"
    )
    headers = await plugin._make_headers()
    if not headers:
        err = getattr(plugin, "_last_token_error", "<未知错误>")
        yield event.plain_result(prefix + f"无法获取 QQ Bot Token，原因: {err}")
        return
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp_guild = await client.get(f"https://api.sgroup.qq.com/guilds/{api_guild_id}", headers=headers)
        if resp_guild.status_code != 200:
            yield event.plain_result(prefix + f"获取频道信息失败，状态码 {resp_guild.status_code}，{resp_guild.text}")
            return
        guild_data = resp_guild.json()
        resp_members = await client.get(f"https://api.sgroup.qq.com/guilds/{api_guild_id}/members?limit=100", headers=headers)
        member_names = [m.get("nick", m.get("user", {}).get("username", "未知")) for m in (resp_members.json() if resp_members.status_code == 200 else [])] or ["<成员列表获取失败>"]
    info = [
        f"频道名称: {guild_data.get('name')}",
        f"频道ID: {guild_data.get('id')}",
        f"频道头像: {guild_data.get('icon') or '无'}",
        f"所有者ID: {guild_data.get('owner_id')}",
        f"是否创建者: {guild_data.get('owner')}",
        f"加入时间: {guild_data.get('joined_at')}",
        f"成员总数: {guild_data.get('member_count')}",
        f"最大成员数: {guild_data.get('max_members')}",
        f"描述: {guild_data.get('description') or '无'}",
        f"取到成员数(前100): {len(member_names)}",
        "成员列表: " + ", ".join(member_names)
    ]
    yield event.plain_result(prefix + "\n".join(info))

async def debug_platforms_impl(plugin, event: AstrMessageEvent):
    '''频道管理：列出所有已加载的平台适配器及其配置'''  
    insts = plugin.context.platform_manager.get_insts()
    lines = []
    for p in insts:
        name = getattr(p, 'name', None) or getattr(p, 'id', '<unknown>')
        cfg = getattr(p, 'config', {})
        lines.append(f"{name}: {cfg}")
    yield event.plain_result("\n".join(lines) or "无已加载平台实例。") 