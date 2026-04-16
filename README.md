# QQ Group Bot

A starter NoneBot2 QQ group bot powered by LLOneBot.

## Built-in Features

- `帮助` / `菜单`: show available commands
- `ping`: check whether the bot is online
- `签到`: daily check-in with streak counter
- `roll`: random number, for example `roll 1 100`
- welcome message for new members
- admin commands: `开启功能 <功能名>` and `关闭功能 <功能名>`

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
