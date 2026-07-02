from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import asyncio
from config import TELEGRAM_BOT_TOKEN, ADMIN_IDS, PAYPAL_LINK, PAYPAL_EMAIL, FREE_TIER_LIMIT
from database import Database
from crypto_guardian import CryptoGuardian
from fed_decoder import FedDecoder
from session_sniper import SessionSniper

db = Database()
crypto_guardian = CryptoGuardian()
fed_decoder = FedDecoder()
session_sniper = SessionSniper()

ADMIN_ID_LIST = [int(id.strip()) for id in ADMIN_IDS.split(',')]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
👋 Welcome {user.first_name}!

🛡️ *TradeShield AI*

📊 *Features:*
✅ Scan smart contracts
✅ Analyze Fed statements  
✅ Get trading session times

💰 *Pricing:*
 Free: {FREE_TIER_LIMIT} checks/day
⭐ VIP: Unlimited ($35/month)

Use /menu to start!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Scan Contract", callback_data='scan')],
        [InlineKeyboardButton("🏛️ Fed Decoder", callback_data='fed')],
        [InlineKeyboardButton("⏰ Sessions", callback_data='sessions')],
        [InlineKeyboardButton("👑 VIP", callback_data='vip')],
        [InlineKeyboardButton("📊 Stats", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Scan Contract", callback_data='scan')],
        [InlineKeyboardButton("🏛️ Fed Decoder", callback_data='fed')],
        [InlineKeyboardButton("⏰ Sessions", callback_data='sessions')],
        [InlineKeyboardButton("👑 VIP", callback_data='vip')],
        [InlineKeyboardButton("📊 Stats", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📱 *Main Menu*", parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'scan':
        await query.message.reply_text("🔍 *Scan Contract*\n\nSend contract address:\n`0x...`", parse_mode='Markdown')
    
    elif query.data == 'fed':
        await query.message.reply_text("🏛️ *Fed Decoder*\n\nPaste Fed statement text.", parse_mode='Markdown')
    
    elif query.data == 'sessions':
        best_times = session_sniper.get_best_times()
        text = "⏰ *Best Trading Times*\n\n"
        for s in best_times:
            text += f"📌 *{s['name']}*\n⏱️ {s['time']}\n{s['description']}\n💱 {s['pairs']}\n\n"
        await query.message.reply_text(text, parse_mode='Markdown')
    
    elif query.data == 'vip':
        text = f"""
👑 *VIP Upgrade - $35/month*

✅ Unlimited scans
✅ Priority AI
✅ Full history

*How to subscribe:*
1. Pay: {PAYPAL_LINK}
2. Send: /verify your@email.com
        """
        keyboard = [[InlineKeyboardButton("💳 Pay PayPal", url=PAYPAL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'stats':
        user = db.get_user(user_id)
        if user:
            is_vip = db.is_vip(user_id)
            text = f"📊 *Your Stats*\n\n👤 ID: `{user_id}`\n⭐ {'VIP 👑' if is_vip else 'Free 🆓'}\n"
            if not is_vip:
                text += f"📊 Checks: {user[5]}/{FREE_TIER_LIMIT}\n"
            text += f"📅 Joined: {user[7]}"
            await query.message.reply_text(text, parse_mode='Markdown')
    
    elif query.data == 'help':
        await query.message.reply_text("📖 Use /start, /menu, /vip, /verify, /stats")

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: /verify your@email.com")
        return
    
    email = context.args[0]
    db.add_verification_request(user_id, email)
    
    for admin_id in ADMIN_ID_LIST:
        try:
            await context.bot.send_message(admin_id, f"🆕 New VIP Request\n\n👤 {update.effective_user.first_name}\n🔢 ID: `{user_id}`\n📧 {email}\n\n/activate {user_id}", parse_mode='Markdown')
        except: pass
    
    await update.message.reply_text(f"✅ Request sent!\n📧 {email}\n⏳ Admin will review soon.")

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID_LIST:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /activate USER_ID")
        return
    
    target_id = int(context.args[0])
    db.activate_vip(target_id, 30)
    await update.message.reply_text(f"✅ VIP activated for {target_id}!")
    
    try:
        await context.bot.send_message(target_id, "🎉 *VIP Activated!*\n\n👑 Unlimited access for 30 days!", parse_mode='Markdown')
    except: pass

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID_LIST:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    pending = db.get_pending_verifications()
    if not pending:
        await update.message.reply_text("✅ No pending requests")
        return
    
    text = "📬 *Pending:*\n\n"
    for req in pending:
        text += f"👤 {req[0]} - {req[1]}\n✅ /activate {req[0]}\n\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if not db.can_check(user_id):
        await update.message.reply_text(f"❌ Limit reached! Upgrade: /vip")
        return
    
    await update.message.reply_text("🔍 Scanning...")
    result = await crypto_guardian.scan_contract(text)
    
    if result['success']:
        db.increment_check(user_id)
        emoji = "🟢" if result['risk_level'] == 'Low' else "🟡" if result['risk_level'] == 'Medium' else "🔴"
        report = f"{emoji} *Scan Report*\n\n📝 `{result['address']}`\n⚠️ Risk: *{result['risk_level']}*\n✅ Verified: {result['verified']}\n\n*Issues:*\n"
        for issue in result['issues']:
            report += f"{issue}\n"
        await update.message.reply_text(report, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ Error: {result.get('error')}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('0x') and len(text) == 42:
        await handle_address(update, context)
    else:
        await update.message.reply_text("🤔 Try: /start, /menu, or send contract address")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(CommandHandler('verify', verify_command))
    application.add_handler(CommandHandler('activate', activate_command))
    application.add_handler(CommandHandler('pending', pending_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 TradeShield AI Bot running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    finally:
        db.close()
