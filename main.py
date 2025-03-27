from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from .Commands import answer_book_command
from .Commands.story import one_sentence_story_command
import astrbot.api.message_components as Comp

@register("wanbot1", "YourName", "一个带有多个实用功能的插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
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

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
