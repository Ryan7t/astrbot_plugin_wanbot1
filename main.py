from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from .Commands import answer_book_command
from .Commands.story import one_sentence_story_command
from .Commands.fortune import fortune_command
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig

# 启动命令
# 在D:\桌面\机器人\AstrBotLauncher-0.1.5.5目录下运行以下命令：
# D:\桌面\机器人\AstrBotLauncher-0.1.5.5\launcher_astrbot_en.bat

@register("wanbot1", "YourName", "一个带有多个实用功能的插件", "1.0.0")
class MyPlugin(Star):
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

    # ----------------- QQ 频道相关功能  -----------------

    async def _fetch_members_count(self, channel_id: str):
        """使用 AstrBot QQOFFICIAL 适配器拉取成员数量 (已由框架封装鉴权)。"""
        from astrbot.api.event import filter as _f  # 避免顶部命名冲突

        platform = self.context.get_platform(_f.PlatformAdapterType.QQOFFICIAL)
        if not platform:
            raise RuntimeError("当前未加载 QQ 官方平台适配器")

        client = platform.get_client()

        limit = 1000
        after = None
        total = 0

        while True:
            params = {"limit": str(limit)}
            if after:
                params["after"] = after
            resp = await client.request("GET", f"/channels/{channel_id}/members", params=params)
            members = resp or []
            total += len(members)
            if len(members) < limit:
                break
            after = members[-1]["user"]["id"]
        return total

    async def _kick_member(self, channel_id: str, user_id: str, reason: str = "", delete_days: int = 7):
        """调用 AstrBot QQOFFICIAL 客户端踢人接口。"""
        from astrbot.api.event import filter as _f

        platform = self.context.get_platform(_f.PlatformAdapterType.QQOFFICIAL)
        if not platform:
            raise RuntimeError("当前未加载 QQ 官方平台适配器")

        client = platform.get_client()

        payload = {
            "add_blacklist": True,
            "delete_history_msg_days": delete_days,
            "reason": reason,
        }

        await client.request("DELETE", f"/channels/{channel_id}/members/{user_id}", json=payload)

    @filter.command("获取频道成员数量")
    async def cmd_get_member_count(self, event: AstrMessageEvent):
        """获取当前子频道成员数量"""
        try:
            channel_id = event.get_group_id() or event.message_obj.group_id
            if not channel_id:
                yield event.plain_result("无法识别当前频道 ID")
                return

            count = await self._fetch_members_count(channel_id)
            yield event.plain_result(f"当前频道成员数量：{count} 人")
        except Exception as e:
            print(f"获取频道成员数量异常: {e}")
            yield event.plain_result(f"获取成员数量失败: {e}")

    @filter.command("移除")
    async def cmd_remove_member(self, event: AstrMessageEvent):
        """按格式 /移除 <原因> @成员  移出频道成员"""
        try:
            msg = event.message_str.strip()
            parts = msg.split()
            if len(parts) < 2:
                yield event.plain_result("格式错误，应为：/移除 <原因> @成员")
                return

            # 去掉指令本身
            parts = parts[1:]

            # 提取 @ 成员
            at_members = [comp.qq for comp in event.get_messages() if isinstance(comp, Comp.At)]
            if not at_members:
                yield event.plain_result("请 @ 需要移除的成员")
                return

            # 剩余文本视为原因
            reason_words = [p for p in parts if not p.startswith("@")]  # 去掉纯 @xxx 文本
            reason = " ".join(reason_words) or "无"

            channel_id = event.get_group_id() or event.message_obj.group_id
            if not channel_id:
                yield event.plain_result("无法识别当前频道 ID")
                return

            success = []
            failed = []
            for uid in at_members:
                try:
                    await self._kick_member(channel_id, uid, reason)
                    success.append(uid)
                except Exception as e:
                    failed.append((uid, str(e)))

            msg_parts = []
            if success:
                msg_parts.append(f"已移除成员: {', '.join(success)}")
            if failed:
                msg_parts.append("移除失败:\n" + "\n".join([f"{u}: {err}" for u, err in failed]))
            yield event.plain_result("\n".join(msg_parts))
        except Exception as e:
            print(f"移除成员异常: {e}")
            yield event.plain_result(f"移除成员失败: {e}")

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
