import asyncio
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler   # pip install apscheduler
from astrbot.api.star import Star, register, Context
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger
from astrbot.api.message_components import Plain, Image
from astrbot.api.all import AstrBotConfig

@register("xhs_demo", "your_name", "每日自动小红书推广", "1.0.0", "")
class XhsPlugin(Star):
    def __init__(self, ctx: Context, cfg: AstrBotConfig):
        super().__init__(ctx)
        self.cfg = cfg
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self._schedule_task()
        self.scheduler.start()
        logger.info("[xhs_auto] 每日推送任务已启动")

    # ---------- 定时任务 ----------
    def _schedule_task(self):
        hour, minute = map(int, self.cfg["push_time"].split(":"))
        self.scheduler.add_job(
            self._daily_push,
            trigger="cron",
            hour=hour,
            minute=minute,
            id="xhs_daily_push",
            replace_existing=True,
        )

    async def _daily_push(self):
        targets = self.cfg["targets"]
        text = self.cfg["push_text"]
        img  = self.cfg["push_image"]
        chain = [Plain(text), Image.fromURL(img)]

        logger.info(f"[xhs_auto] 开始推送，目标 {targets}")
        for umo in targets:
            try:
                await self.context.send_message(umo, chain)
                logger.info(f"[xhs_auto] 已推送至 {umo}")
            except Exception as e:
                logger.exception(f"[xhs_auto] 推送到 {umo} 失败: {e}")

    # ---------- 手动指令 ----------
    @filter.command("xhs_add")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def cmd_add(self, event: AstrMessageEvent):
        """把当前会话加入每日推送列表"""
        umo = event.unified_msg_origin
        if umo in self.cfg["targets"]:
            yield event.plain_result("该会话已在推送列表中！")
            return

        self.cfg["targets"].append(umo)
        self.cfg.save_config()
        yield event.plain_result("✅已加入每日 10:00 推送列表！")

    @filter.command("xhs_remove")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def cmd_remove(self, event: AstrMessageEvent):
        """把当前会话从推送列表移除"""
        umo = event.unified_msg_origin
        if umo not in self.cfg["targets"]:
            yield event.plain_result("该会话不在推送列表！")
            return

        self.cfg["targets"].remove(umo)
        self.cfg.save_config()
        yield event.plain_result("❌已移出推送列表！")

    # ---------- 优雅退出 ----------
    async def terminate(self):
        self.scheduler.shutdown()
        logger.info("[xhs_auto] 定时任务已停止")

    @filter.command("xhs_push_now")
    # 如果只想让管理员用，保留下面一行；否则删掉
    # @filter.permission_type(filter.PermissionType.ADMIN)
    async def cmd_push_now(self, event: AstrMessageEvent):
        """立即手动推送今日内容到当前会话"""
        umo = event.unified_msg_origin
        text = self.cfg["push_text"]
        img  = self.cfg["push_image"]
        chain = [Plain(text), Image.fromURL(img)]

        try:
            # 直接发送
            await self.context.send_message(umo, chain)
            # 给用户一个反馈
            yield event.plain_result("✅ 推送成功！")
            logger.info(f"[xhs_auto] 手动推送成功至 {umo}")
        except Exception as e:
            yield event.plain_result("❌ 推送失败，请查看日志")
            logger.exception(f"[xhs_auto] 手动推送失败: {e}")
