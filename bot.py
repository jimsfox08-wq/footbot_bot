import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "9283403418:AAGHjaKFs8PcIqmD1-MHfT5sNKUZO4Xbeb4"
ADMIN_ID = 7708624515
CHANNEL_USERNAME = "@foot360foot"
CHANNEL_LINK = "https://t.me/foot360foot"

PRICES = {
    "semaine": {"label": "1 Semaine - 2.000 FCFA", "price": 2000},
    "mois": {"label": "1 Mois - 5.000 FCFA", "price": 5000},
    "saison": {"label": "Toute la Saison - 15.000 FCFA", "price": 15000},
}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 1 Semaine - 2.000 FCFA", callback_data="buy_semaine")],
        [InlineKeyboardButton("📦 1 Mois - 5.000 FCFA", callback_data="buy_mois")],
        [InlineKeyboardButton("👑 Toute la Saison - 15.000 FCFA", callback_data="buy_saison")],
    ]
    await update.message.reply_text(
        "⚽ *Bienvenue sur 360FOOT+ VIP* ⚽\n\n"
        "Choisis ton abonnement :",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data.replace("buy_", "")
    context.user_data["plan"] = plan
    info = PRICES[plan]
    await query.message.reply_text(
        f"✅ Tu as choisi : *{info['label']}*\n\n"
        f"📱 *PAIEMENT MOBILE MONEY :*\n"
        f"1. Envoie *{info['price']} FCFA* sur :\n"
        f"MTN MoMo / Orange Money : *[METS TON NUMÉRO ICI]*\n"
        f"Nom : *[TON NOM]*\n\n"
        f"2. Fais une capture d'écran\n"
        f"3. Envoie-la ici",
        parse_mode="Markdown"
    )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = context.user_data.get("plan", "inconnu")
    info = PRICES.get(plan, {"label": plan})
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("✅ Valider", callback_data=f"validate_{user.id}_{plan}")],
        [InlineKeyboardButton("❌ Refuser", callback_data=f"refuse_{user.id}")],
    ]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 *NOUVEAU PAIEMENT*\n\nUser : @{user.username} ({user.id})\nNom : {user.full_name}\nPlan : {info['label']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await update.message.reply_text("📩 Preuve envoyée ! Attends la validation.")

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    data = query.data.split("_")
    action = data[0]
    target_id = int(data[1])
    if action == "validate":
        try:
            invite = await context.bot.create_chat_invite_link(chat_id=CHANNEL_USERNAME, member_limit=1)
            link = invite.invite_link
        except Exception:
            link = CHANNEL_LINK
        await context.bot.send_message(chat_id=target_id, text=f"🎉 *PAIEMENT VALIDÉ !*\n\nVoici ton lien unique :\n{link}", parse_mode="Markdown")
        await query.message.reply_text(f"✅ Validé pour {target_id}")
    else:
        await context.bot.send_message(chat_id=target_id, text="❌ Paiement refusé. Contacte le support.")
        await query.message.reply_text(f"❌ Refusé pour {target_id}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_handler, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(admin_handler, pattern="^(validate|refuse)_"))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()
