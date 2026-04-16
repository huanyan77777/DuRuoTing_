﻿# QQ Group Bot

用在QQ群聊的NoneBot2机器人。
A starter NoneBot2 QQ group bot powered by LLOneBot.

## Built-in Features



## Before Running

1. Start `LLOneBot`
2. Make sure reverse WebSocket points to `ws://127.0.0.1:8080/onebot/v11/ws`
3. Install dependencies, then run `python bot.py`

## Project Layout

```text
bot.py
src/plugins/
data/
```

### 需要手动补充的东西： 

##### .env
```text
DRIVER=~fastapi+~websockets
HOST=127.0.0.1
PORT= //
LOG_LEVEL=INFO
analysis_display_image=true
analysis_display_image_list=["video","bangumi","live","article","dynamic"]

SUPERUSERS=["242003347"]  # 替换为你的超级用户 QQ 号列表

ONEBOT_ACCESS_TOKEN=
LOCALSTORE_USE_CWD=true

# DeepSeek 人格闲聊配置
DEEPSEEK_API_KEY= # 替换为你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner (or deepseek-chat)
DU_RUO_TING_PERSONA_PATH=D:\nonebot\杜若汀.txt (or ...)
DU_RUO_TING_REPLY_PROBABILITY=0.08 (日常回复的概率)
DU_RUO_TING_DIRECT_REPLY_PROBABILITY=0.72 (提到“杜若汀”回复的概率)
DU_RUO_TING_MIN_REPLY_INTERVAL_SECONDS=1000
DU_RUO_TING_SUMMARY_INTERVAL_MINUTES=30
DU_RUO_TING_RECENT_CONTEXT_MESSAGES=10
DU_RUO_TING_MAX_REPLY_CHARS=90

```