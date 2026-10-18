# 个人对局数据

用于路线图第 2 项：估计本人的实力与波动范围。

- 原始导出文件放 `data/private/`（已在 `.gitignore` 中，默认不提交）。
- 整理成 `template_matches.csv` 的格式后再分析；一行一局，按时间排序。

| 字段 | 必填 | 说明 |
|---|---|---|
| `game` | 是 | 游戏名，如 `lol`、`valorant`、`dota2`、`cs2`、`hs_bg`、`hok` |
| `mode` | 是 | 模式，如 `ranked_solo`、`ranked_flex`、`bg_solo` |
| `match_id` | 否 | 游戏内对局编号，便于去重 |
| `start_time` | 是 | 开始时间，ISO 8601，带时区，如 `2026-10-18T21:05:00+08:00` |
| `duration_min` | 否 | 时长（分钟） |
| `result` | 是 | `win` / `loss` / `draw`；名次制游戏可留空 |
| `placement` | 否 | 名次（酒馆战棋 1–8） |
| `players_per_match` | 是 | 每局人数（1v1=2，5v5=10，酒馆战棋=8） |
| `rank_before` | 否 | 赛前段位或显示分 |
| `rating_before` / `rating_after` | 否 | 赛前/赛后分数（显示分或可得的 MMR） |
| `team_avg_rating` / `opp_avg_rating` | 否 | 己方/对方平均分（检验“控胜率”说法最需要的字段） |
| `party_size` | 否 | 组队人数（单排=1） |
| `hero_or_role` | 否 | 英雄/角色/流派 |
| `queue_time_s` | 否 | 排队时长（秒） |
| `session_id` | 否 | 同一次连续游玩的编号（间隔超过 30 分钟算新的一次） |
| `notes` | 否 | 备注，如“掉线”“有人挂机” |
