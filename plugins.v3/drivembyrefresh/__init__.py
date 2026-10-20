import time
from typing import Any, List, Dict, Tuple

from app.core.event import eventmanager
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType
from app.utils.http import RequestUtils


class DrivembyRefresh(_PluginBase):
    # 插件名称
    plugin_name = "Drivemby刷新"
    # 插件描述
    plugin_desc = "媒体文件整理完成后通知Drivemby增量刷新媒体库"
    # 插件图标
    plugin_icon = "refresh.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "Clsital"
    # 作者主页
    author_url = "https://github.com/Clsital"
    # 插件配置项ID前缀
    plugin_config_prefix = "drivembyrefresh_"
    # 加载顺序
    plugin_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _token = ""
    _path = "/影视"
    # ponytail: 全局冷却去重（刷新路径固定，合并突发整理事件的重复通知）；需要逐条秒级通知时改为按路径去重
    _cooldown_seconds = 15
    _last_notify_at = 0.0

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._token = config.get("token") or ""
            self._path = config.get("path") or "/影视"

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [{
            "cmd": "/drivemby_refresh",
            "event": EventType.PluginAction,
            "desc": "测试通知Drivemby刷新",
            "category": "",
            "data": {
                "action": "drivemby_refresh"
            }
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'token',
                                            'label': 'Drivemby API令牌',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'path',
                                            'label': '刷新路径（网盘目录或其上级目录）',
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "token": "",
            "path": "/影视"
        }

    def get_page(self) -> List[dict]:
        pass

    def _notify(self) -> None:
        """向Drivemby发送增量刷新通知"""
        if not self._token:
            logger.error("[Drivemby] 未配置API令牌，跳过刷新通知")
            return
        try:
            ret = RequestUtils(
                content_type="application/json",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=15,
            ).post_res("https://drivemby.com/api/hooks/refresh",
                       json={"path": self._path})
        except Exception as e:
            logger.error(f"[Drivemby] 刷新通知异常: {e}")
            return
        if ret is None:
            logger.error("[Drivemby] 刷新通知失败: 无响应")
        elif ret.status_code == 200:
            logger.info(f"[Drivemby] 已通知刷新: {self._path}")
        else:
            logger.error(f"[Drivemby] 刷新通知失败: {ret.status_code} {ret.text[:200]}")

    @eventmanager.register(EventType.TransferComplete)
    def on_transfer_complete(self, event):
        """整理完成后通知Drivemby刷新"""
        if not self._enabled:
            return
        now = time.time()
        if now - self._last_notify_at < self._cooldown_seconds:
            return
        self._last_notify_at = now
        self._notify()

    @eventmanager.register(EventType.PluginAction)
    def on_action(self, event):
        """测试命令：立即发送一次刷新通知"""
        if event and event.event_data \
                and event.event_data.get("action") == "drivemby_refresh":
            self._notify()

    def stop_service(self):
        pass
