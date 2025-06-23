
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import sqlite3
import datetime

API_TOKEN = "YOUR_BOT_TOKEN_HERE"  # استبدل هذا لاحقًا في config.py

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# قاعدة البيانات
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_claim TEXT,
    referrals INTEGER DEFAULT 0
)''')
conn.commit()

# الأزرار الرئيسية
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🎮 بدء التعدين", "📦 الباقات")
main_menu.add("👥 فريقي", "💼 المحفظة")
main_menu.add("💸 سحب", "🔁 تحويل")

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    await message.answer("👋 أهلاً بك في Empire Mining Bot
اختر من القائمة:", reply_markup=main_menu)

@dp.message_handler(lambda message: message.text == "🎮 بدء التعدين")
async def mine(message: types.Message):
    user_id = message.from_user.id
    now = datetime.datetime.now()
    cursor.execute("SELECT last_claim FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        last_claim = datetime.datetime.fromisoformat(row[0])
        diff = (now - last_claim).total_seconds()
        if diff < 86400:
            remaining = int((86400 - diff) / 60)
            return await message.answer(f"⏳ يمكنك المطالبة مجددًا بعد {remaining} دقيقة.")
    cursor.execute("UPDATE users SET balance = balance + 1000, last_claim = ? WHERE user_id=?",
                   (now.isoformat(), user_id))
    conn.commit()
    await message.answer("✅ تم إضافة 1000 SOT إلى رصيدك!")

@dp.message_handler(lambda message: message.text == "💼 المحفظة")
async def wallet(message: types.Message):
    await message.answer(
        "💼 محفظتك:

"
        "🔹 TRC20: TJj1Mb77hoSC5PbPiT4pc9oqMzvNS1V5Q3
"
        "🔸 BEP20: 0xb2d1e9ec71199a32551b8d5dd1826e00c1e2d9a4"
    )

@dp.message_handler(lambda message: message.text == "🔁 تحويل")
async def convert(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    usdt = (balance // 10000) * 10
    await message.answer(f"💱 تم تحويل رصيدك إلى {usdt} USDT (تقريباً)")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
