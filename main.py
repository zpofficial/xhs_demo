# main.py
from astrbot.api.star import Star, register, Context
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger
import astrbot.api.message_components as Comp


@register("xhs_demo", "your_name", "一个 /xhs 指令示例", "1.0.0", "")
class XhsPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 注册 /xhs 命令
    @filter.command("xhs")
    async def cmd_xhs(self, event: AstrMessageEvent):
        """
        机器人立即回复一条小红书风格的消息
        """
        logger.info(f"用户 {event.get_sender_name()} 触发了 /xhs")

        # 1. 纯文本
        text = "🌸今日份小红书推送🌸\n———————————————\n姐妹们这条连衣裙真的绝绝子！💃\n显瘦 10 斤不是梦！"

        # 2. 图片（可换成你自己的 URL 或本地路径）
        image_url = "https://picasso-static.xiaohongshu.com/fe-platform/2b145902e47cfe2c7843282b22bbe69e9541215c.png"

        # 3. 组装消息链
        chain = [
            Comp.Plain(text),
            Comp.Image.fromURL(image_url),
            Comp.Plain("\n姐妹们冲鸭！🛒")
        ]

        # 4. 发送
        yield event.chain_result(chain)
