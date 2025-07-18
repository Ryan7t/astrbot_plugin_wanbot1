from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from .Commands import answer_book_command
from .Commands.story import one_sentence_story_command
from .Commands.fortune import fortune_command
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
import httpx  # 新增: 用于异步 HTTP 请求
import time  # 新增，用于缓存 token 过期时间
from .Commands.channel_management import (
    get_guild_details_impl,
    kick_member_impl,
    kick_member_inline_impl,
    debug_platforms_impl,
)

# 启动命令
# 在D:\桌面\机器人\AstrBotLauncher-0.1.5.5目录下运行以下命令：
# D:\桌面\机器人\AstrBotLauncher-0.1.5.5\launcher_astrbot_en.bat

@register("wanbot1", "YourName", "一个带有多个实用功能的插件", "1.0.0")
class MyPlugin(Star):
    # 待办事项:
    # - 完善踢出逻辑，确保兼容各种 @ 格式和纯数字 ID
    # - 增加对接口错误码的友好提示和重试机制
    # - 添加单元测试覆盖 /获取频道详细 和 /踢出 命令
    # - 优化日志输出，方便调试和运维
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config
        print(f"wanbot1插件配置: {self.config}")
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        print(f"收到消息链: {message_chain}")
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    @filter.command("userinfo")
    async def userinfo(self, event: AstrMessageEvent):
        '''获取用户信息的指令，显示当前用户的所有可用信息'''
        # 获取用户基本信息
        user_id = event.get_sender_id()
        user_name = event.get_sender_name()
        
        # 获取消息相关信息
        message_obj = event.message_obj
        sender_info = message_obj.sender
        
        # 构建信息字符串
        info_str = "用户信息如下：\n"
        info_str += f"用户ID: {user_id}\n"
        info_str += f"用户名称: {user_name}\n"
        
        # 添加消息对象中的信息
        info_str += f"消息ID: {message_obj.message_id}\n"
        info_str += f"会话ID: {message_obj.session_id}\n"
        info_str += f"自身ID: {message_obj.self_id}\n"
        info_str += f"群组ID: {message_obj.group_id}\n"
        info_str += f"时间戳: {message_obj.timestamp}\n"
        
        # 添加发送者详细信息
        info_str += f"发送者详细信息:\n"
        info_str += f"  群名片: {sender_info.display_name if hasattr(sender_info, 'display_name') else '无'}\n"
        info_str += f"  权限: {sender_info.permission if hasattr(sender_info, 'permission') else '无'}\n"
        
        # 尝试获取更多可能的发送者信息
        for key, value in vars(sender_info).items():
            if key not in ['display_name', 'permission']:
                info_str += f"  {key}: {value}\n"
        
        # 返回所有信息
        yield event.plain_result(info_str)

    @filter.command("帮助")
    async def help(self, event: AstrMessageEvent):
        '''显示插件的所有可用指令及其使用说明'''
        # 创建帮助信息字符串

        help_text = "🤖 小万bot报错指南 🤖\n\n"
        help_text += "如果遇到以下报错，表示此时与小万聊天的人太多了，请稍等30s后再发送消息，小万真的很舍不得你~\n\n"
        help_text += "报错信息：\n"
        help_text += "```\n"
        help_text += "错误类型: RateLimitError\n"
        help_text += "错误信息: Error code: 429\n"
        help_text += "```\n\n"
        
        help_text += "🤖 小万bot指令使用帮助 🤖\n\n"
        help_text += "注意：每个指令前需添加/作为前缀：\n\n"
        help_text += "使用示例：\n"
        help_text += "/答案之书 我今天会遇到好事吗？\n"
        help_text += "/一句话故事 友情\n"
        help_text += "/今日运势\n\n"
        
        help_text += "🎮 娱乐指令：\n"
        help_text += "➤ 答案之书 [问题] - 提供一个问题，获得神秘答案\n"
        help_text += "➤ 一句话故事 [主题] - 提供一个主题，获得一个简短有意思的故事种子\n"
        help_text += "➤ 今日运势 - 获取你的每日运势预测\n"
        

        # 返回帮助信息
        yield event.plain_result(help_text)

    @filter.command("答案之书")
    async def answer_book(self, event: AstrMessageEvent):
        '''答案之书：提供一个问题，获得神秘答案'''
        # 调用外部实现
        async for result in answer_book_command(self, event):
            yield result

    @filter.command("测试图片")
    async def test_image(self, event: AstrMessageEvent):
        '''测试发送图片功能'''
        print("执行测试图片命令")
        
        # 发送本地图片测试
        message2 = [
            Comp.Plain(text="这是一张本地测试图片："),
            Comp.Image(file="data/plugins/astrbot_plugin_wanbot1/test.jpg")
        ]
        yield MessageEventResult(message2)
        
        # 如果需要同时测试网络图片，可以取消下面的注释
        # 发送网络图片测试
        # message = [
        #     Comp.Plain(text="这是一张网络测试图片："),
        #     Comp.Image(file="https://picsum.photos/300/200")
        # ]
        # yield MessageEventResult(message)

    @filter.command("一句话故事")
    async def one_sentence_story(self, event: AstrMessageEvent):
        '''一句话故事：提供一个主题，获得一个简短有意思的故事种子'''
        # 调用外部实现
        async for result in one_sentence_story_command(self, event):
            yield result

    @filter.command("今日运势")
    async def fortune(self, event: AstrMessageEvent):
        '''今日运势：获取你的每日运势预测'''
        # 调用外部实现
        async for result in fortune_command(self, event):
            yield result

    @filter.event_message_type(filter.EventMessageType.ALL, priority=1)
    async def inline_kick_handler(self, event: AstrMessageEvent):
        '''捕获无空格`/踢出@成员`或`/踢出<@!ID>`格式并执行踢人'''  
        # 委托给 channel_management.kick_member_inline_impl
        async for r in kick_member_inline_impl(self, event):
            yield r
  
    @filter.command("获取频道详细")
    async def get_guild_details(self, event: AstrMessageEvent):
        '''获取频道详细信息并展示部分频道成员列表'''
        # 委托给 channel_management.get_guild_details_impl
        async for r in get_guild_details_impl(self, event):
            yield r

    @filter.command("踢出")
    async def kick_member(self, event: AstrMessageEvent, target_user_id: str = ""):
        '''踢出频道成员，用法：1) /踢出 123456  2) /踢出 @成员'''
        # 委托给 channel_management.kick_member_impl
        async for r in kick_member_impl(self, event, target_user_id):
            yield r

    # 兼容“/踢出@成员”或“/踢出<@!ID>”等无空格格式
    @filter.command("踢出")
    async def kick_member_inline(self, event: AstrMessageEvent):
        '''踢出频道成员，无空格格式处理。示例：/踢出<@!123456> 或 /踢出@成员'''
        msg = event.message_str.strip()
        if not msg.startswith("/踢出"):
            return  # 不是目标格式
        # 去掉前缀
        remain = msg[len("/踢出"):]
        # 尝试从文本中直接提取数字 ID
        import re
        m = re.search(r"(\d{5,})", remain)
        target_id = m.group(1) if m else ""
        # 如果文本内没提到数字，再从消息段 At 里找
        if not target_id:
            target_id = next((
                str(getattr(c, "qq", getattr(c, "id", "")))
                for c in event.get_messages() if isinstance(c, Comp.At)
            ), "")
        if not target_id:
            return  # 无有效 ID，不继续执行，由另一个 handler 提示
        # 将解析出的 ID 交给已有带参数的踢出函数复用逻辑
        async for r in self.kick_member(event, target_id):
            yield r

    # @filter.command("调试平台")
    # async def debug_platforms(self, event: AstrMessageEvent):
    #     '''调试命令：列出所有已加载的平台适配器及其配置'''  
    #     # 委托给 Commands/channel_management.debug_platforms_impl
    #     async for r in debug_platforms_impl(self, event):
    #         yield r
    
    def _get_app_credentials(self):
        """从 QQ 官方平台适配器读取 appId 与 Secret"""
        # 获取 QQ 官方平台凭据逻辑：
        # 1. 优先通过 context.get_platform(PlatformAdapterType.QQOFFICIAL) 获取官方适配器实例
        # 2. 尝试 context.get_platform("qq_official") 与 context.get_platform("qqbot")
        # 3. 若仍未获取，则遍历 context.platform_manager.get_insts()，匹配 config.id 或 config.type 前缀
        # 4. 最后从 platform.config 字典中兼容读取字段：appid/appId/app_id 与 secret/clientSecret/client_secret
        try:
            from astrbot.api.event.filter import PlatformAdapterType
            platform = self.context.get_platform(PlatformAdapterType.QQOFFICIAL)
        except Exception:
            platform = None

        if not platform:
            platform = (
                self.context.get_platform("qq_official")
                or self.context.get_platform("qqbot")
            )

        # 若仍未找到，则遍历所有平台实例，通过 config 的 id 或 type 来识别 QQ 官方平台
        if not platform:
            for p in self.context.platform_manager.get_insts():
                cfg = getattr(p, "config", {}) or {}
                pid = cfg.get("id", "")
                ptype = cfg.get("type", "")
                if pid == "qq_official" or (isinstance(ptype, str) and ptype.startswith("qq_official")):
                    platform = p
                    break

        if not platform:
            return None, None
        # 仅允许使用 AstrBot 配置中标准字段 "appid" 与 "secret"，避免因多余字段导致取值混乱。
        app_id = getattr(platform, "appid", None)
        client_secret = getattr(platform, "secret", None)

        # 如果平台实例上未直接提供，则继续从其 config 字典获取
        cfg = getattr(platform, "config", {}) or {}
        # 多种键名兼容
        if not app_id:
            app_id = (
                cfg.get("appid")
                or cfg.get("appId")
                or cfg.get("app_id")
            )
        if not client_secret:
            client_secret = (
                cfg.get("secret")
                or cfg.get("clientSecret")
                or cfg.get("client_secret")
            )
        return app_id, client_secret

    async def _ensure_access_token(self):
        """确保获取/缓存 access_token。"""
        app_id, client_secret = self._get_app_credentials()
        if not app_id or not client_secret:
            return ""
        cache = getattr(self, "_qqbot_token_cache", None)
        now = time.time()
        if cache and cache.get("expire", 0) > now + 60:
            return cache["token"]
        url = "https://bots.qq.com/app/getAppAccessToken"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"appId": app_id, "clientSecret": client_secret})
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token")
                # 若接口返回中未包含 token，则视为异常
                if not token:
                    self._last_token_error = f"API返回异常: {data}"
                    return ""
                expires = int(data.get("expires_in", 7000))
                self._qqbot_token_cache = {"token": token, "expire": now + expires}
                return token
            else:
                # HTTP 状态非 200，保存错误信息并返回
                self._last_token_error = f"HTTP {resp.status_code} {resp.text}"
                return ""
        except Exception as e:
            # 保存异常信息供上层输出
            self._last_token_error = str(e)
        return ""

    async def _make_headers(self):
        token = await self._ensure_access_token()
        if not token:
            # _ensure_access_token 内部会将错误信息存到 _last_token_error
            return None
        return {
            "Authorization": f"QQBot {token}",
            "User-Agent": "AstrBotPlugin wanbot1/1.0.0",
            "Content-Type": "application/json",
        }

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
