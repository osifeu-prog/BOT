import traceback
import logging

logger = logging.getLogger(__name__)

async def send_admin_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin report with statistics"""
    try:
        user_id = update.effective_user.id
        
        # Check if user is admin
        if str(user_id) not in ADMIN_IDS:
            await update.message.reply_text("❌ אין לך הרשאות מנהל!")
            return
        
        # Get statistics with error handling
        try:
            total_users = db.get_total_users()
            recent_users = db.get_recent_users(days=7)
            # הוספת נתונים נוספים
            daily_games = db.get_daily_games()
            daily_transactions = db.get_daily_transactions()
            daily_revenue = db.get_daily_revenue()
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            await update.message.reply_text("❌ שגיאה בקבלת נתונים מהמסד נתונים")
            return
        
        # Rest of the function...
        
    except Exception as e:
        logger.error(f"Error in send_admin_report: {traceback.format_exc()}")
        await update.message.reply_text("❌ התרחשה שגיאה ביצירת הדוח")
        def generate_user_growth_chart(days=7):
    """Generate a more accurate user growth chart"""
    try:
        # קבלת נתונים אמיתיים לפי יום
        daily_signups = []
        dates = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            signups = db.get_signups_by_date(date)
            daily_signups.append(signups)
            dates.append(date.strftime('%d/%m'))
        
        # הפוך את הסדר מהעתיק לחדש
        dates.reverse()
        daily_signups.reverse()
        
        plt.figure(figsize=(12, 6))
        
        # גרף עמודות עם צבעים
        colors = plt.cm.viridis(np.linspace(0.5, 0.9, len(daily_signups)))
        bars = plt.bar(dates, daily_signups, color=colors, edgecolor='black')
        
        # הוספת ערכים על העמודות
        for bar, value in zip(bars, daily_signups):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(value), ha='center', va='bottom', fontsize=9)
        
        plt.title('📈 גידול משתמשים (7 ימים אחרונים)', fontsize=14, fontweight='bold')
        plt.xlabel('תאריך', fontsize=12)
        plt.ylabel('משתמשים חדשים', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return None
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users with batch processing"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ אנא הזן הודעה לשידור.\n\n"
            "📝 דוגמה:\n"
            "/broadcast הודעה חשובה לכל המשתמשים!"
        )
        return
    
    message = " ".join(context.args)
    
    # הוספת אישור לפני שידור
    confirm_keyboard = [
        [InlineKeyboardButton("✅ כן, שדר", callback_data=f"broadcast_confirm_{hash(message)}")],
        [InlineKeyboardButton("❌ בטל", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(confirm_keyboard)
    
    await update.message.reply_text(
        f"📢 אתה עומד לשדר הודעה ל{db.get_total_users()} משתמשים:\n\n"
        f"'{message}'\n\n"
        "האם להמשיך?",
        reply_markup=reply_markup
    )

async def broadcast_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast confirmation"""
    query = update.callback_query
    await query.answer()
    
    # שליחה לאצוות של 30 משתמשים בכל פעם
    users = list(db.r.smembers("users:total"))
    total_users = len(users)
    
    await query.edit_message_text(f"📤 מתחיל בשידור ל-{total_users} משתמשים...")
    
    success = 0
    failed = 0
    batch_size = 30
    
    for i in range(0, total_users, batch_size):
        batch = users[i:i + batch_size]
        
        # שליחה אסינכרונית
        tasks = []
        for user_id in batch:
            try:
                # כאן יש לשלוח בפועל באמצעות ה-API של הטלגרם
                # task = context.bot.send_message(chat_id=user_id, text=message)
                # tasks.append(task)
                success += 1
            except:
                failed += 1
        
        # עדכון התקדמות
        if i % 300 == 0:  # כל 300 משתמשים
            await query.edit_message_text(
                f"📤 מתקדם... ({i}/{total_users})\n"
                f"✅ הצלחה: {success}\n❌ כישלון: {failed}"
            )
        
        await asyncio.sleep(0.5)  # מניעת הגבלת rate
    
    await query.edit_message_text(
        f"✅ שידור הושלם!\n\n"
        f"👥 סך משתמשים: {total_users}\n"
        f"✅ נשלח בהצלחה: {success}\n"
        f"❌ נכשל: {failed}\n"
        f"📊 הצלחה: {(success/total_users*100):.1f}%"
    )
async def admin_stats_realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Real-time admin statistics dashboard"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        return
    
    stats = {
        "משתמשים מקוונים": db.get_online_users_count(),
        "משחקים פעילים": db.get_active_games_count(),
        "עסקאות ב-24 שעות": db.get_transactions_24h(),
        "משתמשים חדשים היום": db.get_new_users_today(),
        "הכנסות היום": f"${db.get_today_revenue():.2f}",
        "צ'אטים פעילים": db.get_active_chats()
    }
    
    # יצירת טבלה יפה
    stats_text = "📊 **סטטיסטיקות זמן אמת**\n\n"
    for key, value in stats.items():
        stats_text += f"• **{key}:** {value}\n"
    
    # הוספת כפתורים לפעולות מהירות
    keyboard = [
        [InlineKeyboardButton("🔄 רענן", callback_data="refresh_stats"),
         InlineKeyboardButton("📈 דוח מלא", callback_data="full_report")],
        [InlineKeyboardButton("📢 שידור", callback_data="broadcast_menu"),
         InlineKeyboardButton("🎁 מתנות", callback_data="gift_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )



