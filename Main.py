from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
REQUIRED_CHANNELS = os.environ.get("REQUIRED_CHANNELS", "").split()

app = Client("RealStarBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

users = {}

async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await app.get_chat_member(channel, user_id)
            if member.status in ("kicked", "left"):
                return False
        except:
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    users.setdefault(user_id, {"referrals": 0})
    
    joined = await check_membership(user_id)
    if not joined:
        buttons = [[InlineKeyboardButton("Join All Channels ✅", url="https://t.me/allselleer")],
                   [InlineKeyboardButton("Ganaa Support", url="https://t.me/ganaasupport")],
                   [InlineKeyboardButton("Oy Baby 💕", url="https://t.me/oy_baby")],
                   [InlineKeyboardButton("✅ I've Joined", callback_data="joined")]]
        await message.reply("Please join all channels to continue:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    ref_id = str(message.text.split(" ")[1]) if len(message.text.split()) > 1 else None
    if ref_id and ref_id.isdigit() and int(ref_id) != user_id:
        ref_id = int(ref_id)
        users.setdefault(ref_id, {"referrals": 0})
        users[ref_id]["referrals"] += 1

    await message.reply(f"Welcome {message.from_user.first_name}!\nUse /profile to see your stats.")

@app.on_callback_query(filters.regex("joined"))
async def joined_callback(client, callback_query):
    user_id = callback_query.from_user.id
    joined = await check_membership(user_id)
    if joined:
        await callback_query.message.edit("✅ You have joined all channels. Use /profile or /leaderboard.")
    else:
        await callback_query.answer("❌ You haven't joined all required channels.", show_alert=True)

@app.on_message(filters.command("profile"))
async def profile(client, message):
    user_id = message.from_user.id
    info = users.get(user_id, {"referrals": 0})
    await message.reply(f"👤 Profile:\nUser: {message.from_user.first_name}\nReferrals: {info['referrals']}")

@app.on_message(filters.command("leaderboard"))
async def leaderboard(client, message):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["referrals"], reverse=True)[:10]
    text = "🏆 Leaderboard:\n"
    for i, (user_id, data) in enumerate(sorted_users, 1):
        text += f"{i}. User {user_id} — {data['referrals']} referrals\n"
    await message.reply(text)

app.run()
