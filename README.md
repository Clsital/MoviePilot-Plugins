# MoviePilot-Plugins

MoviePilot 插件仓库。

## DrivembyRefresh

媒体文件整理完成后通知 [Drivemby](https://drivemby.com) 增量刷新媒体库。

- 监听整理完成事件，POST `https://drivemby.com/api/hooks/refresh`
- 配置项：启用开关、Drivemby API 令牌、刷新路径（网盘目录或其上级目录，默认 `/影视库`）
- 剧集批量整理 15 秒冷却合并，避免重复通知

### 安装

MoviePilot → 插件 → 插件市场设置，添加仓库地址：

```
https://github.com/Clsital/MoviePilot-Plugins
```

然后在插件市场安装「Drivemby刷新」，填入令牌并启用。
