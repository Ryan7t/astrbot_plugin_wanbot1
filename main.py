from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from .Commands import answer_book_command
from .Commands.story import one_sentence_story_command
from .Commands.fortune import fortune_command
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api import logger  # 使用 astrbot 提供的 logger 接口
import re
import requests
import json

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
        help_text += "➤ 获取频道成员数量 - 获取当前频道的成员数量\n"
        help_text += "➤ 移出 [原因] @成员 - 将指定成员移出频道\n"
        

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
            
    @filter.command("获取频道成员数量")
    async def get_members(self, event: AstrMessageEvent):
        '''获取频道成员数量：获取当前频道的成员数量和成员列表'''
        logger.info("开始执行获取频道成员数量命令")
        
        # 获取频道ID
        guild_id = event.message_obj.group_id
        if not guild_id:
            error_msg = "此命令只能在频道中使用"
            logger.error(error_msg)
            yield event.plain_result(error_msg)
            return

        try:
            # 构建请求URL
            base_url = "https://api.sgroup.qq.com"
            api_path = f"/guilds/{guild_id}/members"
            url = base_url + api_path
            
            # 构建请求头
            headers = {
                "Authorization": f"Bot {self.config.get('qq_bot_token', '')}", 
                "Content-Type": "application/json"
            }
            
            # 请求参数
            params = {
                "limit": 400  # 获取最大数量的成员
            }
            
            # 发送请求
            logger.info(f"发送请求：URL={url}, 参数={params}")
            response = requests.get(url, headers=headers, params=params)
            logger.info(f"获取到响应：状态码={response.status_code}")
            
            if response.status_code == 200:
                # 解析响应
                members = response.json()
                member_count = len(members)
                logger.info(f"成功获取成员列表，共{member_count}个成员")
                
                # 构建响应消息
                result_message = f"当前频道共有 {member_count} 个成员\n\n"
                result_message += "成员列表（最多显示前10个）：\n"
                
                # 只显示前10个成员以避免消息过长
                for i, member in enumerate(members[:10]):
                    user = member.get("user", {})
                    username = user.get("username", "未知用户")
                    nick = member.get("nick", "")
                    display_name = nick if nick else username
                    result_message += f"{i+1}. {display_name}\n"
                
                if member_count > 10:
                    result_message += f"... 还有 {member_count - 10} 个成员未显示"
                
                yield event.plain_result(result_message)
            else:
                error_message = f"获取频道成员失败，状态码：{response.status_code}，响应：{response.text}"
                logger.error(error_message)
                yield event.plain_result(f"获取频道成员失败：{response.status_code}")
        except Exception as e:
            error_message = f"获取频道成员时发生异常：{str(e)}"
            logger.error(error_message)
            yield event.plain_result(f"获取频道成员时发生错误：{str(e)}")

    @filter.command("移出")
    async def kick_member(self, event: AstrMessageEvent):
        '''移出：移出指定的频道成员，格式为 /移出 原因 @成员'''
        logger.info("开始执行移出成员命令")
        
        # 获取频道ID
        guild_id = event.message_obj.group_id
        if not guild_id:
            error_msg = "此命令只能在频道中使用"
            logger.error(error_msg)
            yield event.plain_result(error_msg)
            return
        
        # 解析命令参数
        message_str = event.message_str
        message_chain = event.get_messages()
        
        # 检查是否有At消息段
        at_segments = [msg for msg in message_chain if msg.type == "at"]
        if not at_segments:
            error_msg = "使用方法错误：请使用 /移出 原因 @成员"
            logger.error(error_msg)
            yield event.plain_result(error_msg)
            return
        
        # 获取被At的用户ID
        target_user_id = at_segments[0].data.get("qq", "")
        if not target_user_id:
            error_msg = "无法获取目标成员ID"
            logger.error(error_msg)
            yield event.plain_result(error_msg)
            return
        
        # 提取移出原因 (去掉命令和@部分)
        reason = message_str.split(f"@{target_user_id}")[0].strip()
        if reason.startswith("移出 "):
            reason = reason[3:].strip()
            
        logger.info(f"解析出参数：target_user_id={target_user_id}, reason={reason}")
        
        try:
            # 构建请求URL
            base_url = "https://api.sgroup.qq.com"
            api_path = f"/guilds/{guild_id}/members/{target_user_id}"
            url = base_url + api_path
            
            # 构建请求头
            headers = {
                "Authorization": f"Bot {self.config.get('qq_bot_token', '')}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            data = {
                "add_blacklist": True,  # 将用户添加到黑名单
                "delete_history_msg_days": 0  # 不删除历史消息
            }
            
            # 发送请求
            logger.info(f"发送请求：URL={url}, 数据={data}")
            response = requests.delete(url, headers=headers, json=data)
            logger.info(f"获取到响应：状态码={response.status_code}")
            
            if response.status_code == 204:
                success_message = f"已成功将成员移出频道\n原因：{reason}"
                logger.info(success_message)
                yield event.plain_result(success_message)
            else:
                error_message = f"移出成员失败，状态码：{response.status_code}，响应：{response.text}"
                logger.error(error_message)
                yield event.plain_result(f"移出成员失败：{response.status_code}")
        except Exception as e:
            error_message = f"移出成员时发生异常：{str(e)}"
            logger.error(error_message)
            yield event.plain_result(f"移出成员时发生错误：{str(e)}")

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
