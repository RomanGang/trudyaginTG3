
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Set environment variable BOT_TOKEN (or put it into a local .env and export it).")

conn = sqlite3.connect('database/trudyagin.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, telegram_id INTEGER UNIQUE, name TEXT, role TEXT, rating REAL)')
c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, description TEXT, city TEXT, district TEXT, workers_required INTEGER, workers_joined INTEGER, status TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, job_id INTEGER, sender_id INTEGER, message TEXT)')
conn.commit()

c.execute("INSERT OR IGNORE INTO users (telegram_id,name,role,rating) VALUES (123456789,'Admin','admin',5)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Я ищу работу", callback_data='worker')],
        [InlineKeyboardButton("Мне нужен работник", callback_data='employer')],
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url='https://example.com/index.html'))]
    ]
    await update.message.reply_text("Добро пожаловать в Trudyagin", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role = query.data
    telegram_id = query.from_user.id
    name = query.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (telegram_id,name,role,rating) VALUES (?,?,?,5)", (telegram_id,name,role))
    conn.commit()
    await query.edit_message_text(f"Вы зарегистрированы как {role}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
