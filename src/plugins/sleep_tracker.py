from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from statistics import mean
from threading import Lock

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from PIL import Image, ImageDraw, ImageFont


DATA_DIR = Path("data")
SLEEP_PATH = DATA_DIR / "sleep_records.json"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
GOOD_NIGHT = "晚安"
GOOD_MORNING = "早安"
SLEEP_STATS = "睡眠统计"
MY_SLEEP_STATS = "我的睡眠统计"

_lock = Lock()

good_night = on_fullmatch({GOOD_NIGHT}, priority=10, block=True)
good_morning = on_fullmatch({GOOD_MORNING}, priority=10, block=True)
sleep_stats = on_fullmatch({SLEEP_STATS, MY_SLEEP_STATS}, priority=10, block=True)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: dict) -> dict:
    _ensure_parent(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, value: dict) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _now() -> datetime:
    return datetime.now()


def _format_dt(value: datetime) -> str:
    return value.strftime(DATE_FORMAT)


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value, DATE_FORMAT)


def _format_duration(hours: float) -> str:
    minutes = max(0, round(hours * 60))
    h, m = divmod(minutes, 60)
    return f"{h}小时{m}分"


def _get_user_data(user_id: int) -> tuple[dict, dict]:
    with _lock:
        data = _read_json(SLEEP_PATH, {"users": {}})
        user = data["users"].setdefault(str(user_id), {"last_sleep_at": None, "sessions": []})
        return data, user


def _save_user_data(data: dict) -> None:
    with _lock:
        _write_json(SLEEP_PATH, data)


def _record_sleep(user_id: int, sleep_at: datetime) -> tuple[bool, str]:
    data, user = _get_user_data(user_id)
    last_sleep_at = user.get("last_sleep_at")
    if last_sleep_at:
        last_time = _parse_dt(last_sleep_at)
        if (sleep_at - last_time).total_seconds() < 3 * 3600:
            return False, f"你已经记录过晚安了，上次是 {_format_dt(last_time)}。"
    user["last_sleep_at"] = _format_dt(sleep_at)
    _save_user_data(data)
    return True, f"晚安，已记录入睡时间：{sleep_at.strftime('%H:%M')}。"


def _record_wake(user_id: int, wake_at: datetime) -> tuple[bool, str, float | None]:
    data, user = _get_user_data(user_id)
    last_sleep_at = user.get("last_sleep_at")
    if not last_sleep_at:
        return False, "你还没有和小汀说晚安呢", None

    sleep_at = _parse_dt(last_sleep_at)
    duration_hours = (wake_at - sleep_at).total_seconds() / 3600
    if duration_hours <= 0:
        return False, "这次的时间记录有点奇怪 我问问桓衍怎么回事 要不你重新记录一下（？", None

    session = {
        "sleep_at": _format_dt(sleep_at),
        "wake_at": _format_dt(wake_at),
        "duration_hours": round(duration_hours, 2),
    }
    sessions = user.setdefault("sessions", [])
    sessions.append(session)
    user["last_sleep_at"] = None
    user["sessions"] = sessions[-30:]
    _save_user_data(data)

    text = (
        f"早安！你这次睡了 {_format_duration(duration_hours)} 小汀今天也和桓衍一样活力满满喔！\n"
        f"这个时候和小汀说的晚安喔：{sleep_at.strftime('%m-%d %H:%M')}\n"
        f"起床：{wake_at.strftime('%m-%d %H:%M')} 起床了可以来茶馆喝茶聊天喔！"
    )
    return True, text, duration_hours


def _load_sessions(user_id: int) -> list[dict]:
    data, user = _get_user_data(user_id)
    return list(user.get("sessions", []))


def _pick_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in (
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ):
        path = Path(font_path)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _build_stats_image(user_id: int, sessions: list[dict]) -> bytes:
    latest_sessions = sessions[-7:]
    hours_list = [float(item["duration_hours"]) for item in latest_sessions]
    avg_hours = mean(float(item["duration_hours"]) for item in sessions)
    latest_hours = float(sessions[-1]["duration_hours"])

    width, height = 900, 560
    image = Image.new("RGB", (width, height), "#f5efe4")
    draw = ImageDraw.Draw(image)

    title_font = _pick_font(36)
    text_font = _pick_font(24)
    small_font = _pick_font(18)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=28, fill="#fffaf2")
    draw.text((50, 50), "睡眠统计", fill="#3b2f2f", font=title_font)
    draw.text((50, 98), f"QQ: {user_id}", fill="#7a6a58", font=small_font)

    draw.text((50, 150), f"累计记录：{len(sessions)} 次", fill="#4d4036", font=text_font)
    draw.text((50, 190), f"平均睡眠：{avg_hours:.2f} 小时", fill="#4d4036", font=text_font)
    draw.text((50, 230), f"最新一次：{latest_hours:.2f} 小时", fill="#4d4036", font=text_font)

    chart_left = 70
    chart_top = 320
    chart_bottom = 480
    chart_height = chart_bottom - chart_top
    draw.line((chart_left, chart_bottom, width - 70, chart_bottom), fill="#d7c4ac", width=3)

    max_hours = max(max(hours_list), 1.0)
    bar_width = 70
    gap = 28
    for index, item in enumerate(latest_sessions):
        hours = float(item["duration_hours"])
        bar_height = max(8, int((hours / max_hours) * chart_height))
        x1 = chart_left + index * (bar_width + gap)
        y1 = chart_bottom - bar_height
        x2 = x1 + bar_width
        draw.rounded_rectangle((x1, y1, x2, chart_bottom), radius=18, fill="#9dbf9e")
        draw.text((x1 + 10, y1 - 28), f"{hours:.1f}h", fill="#4d4036", font=small_font)
        draw.text((x1 + 8, chart_bottom + 10), item["wake_at"][5:10], fill="#6f5f4f", font=small_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@good_night.handle()
async def handle_good_night(event: GroupMessageEvent) -> None:
    _, text = _record_sleep(event.user_id, _now())
    await good_night.finish(text)


@good_morning.handle()
async def handle_good_morning(event: GroupMessageEvent) -> None:
    _, text, _ = _record_wake(event.user_id, _now())
    await good_morning.finish(text)


@sleep_stats.handle()
async def handle_sleep_stats(event: GroupMessageEvent) -> None:
    sessions = _load_sessions(event.user_id)
    if not sessions:
        await sleep_stats.finish("第一次和小汀问好吗，和今天见到的人说早安晚安会让人变得有精神喔")

    avg_hours = mean(float(item["duration_hours"]) for item in sessions)
    latest = sessions[-1]
    image_bytes = _build_stats_image(event.user_id, sessions)
    summary = (
        f"你已记录 {len(sessions)} 次睡眠\n"
        f"平均睡眠：{avg_hours:.2f} 小时\n"
        f"最新一次：{latest['duration_hours']:.2f} 小时\n"
        f"入睡：{latest['sleep_at'][5:]}\n"
        f"起床：{latest['wake_at'][5:]}"
    )
    await sleep_stats.finish(MessageSegment.text(summary) + MessageSegment.image(image_bytes))
