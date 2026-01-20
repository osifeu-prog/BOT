"""
🏆 NFTY ULTRA PRO - Leaderboard System
מערכת לוח תוצאות מתקדמת עם אנימציות, קטגוריות, ותחרויות בזמן אמת
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from app.database.manager import db

class LeaderboardCategory(Enum):
    """קטגוריות לוח תוצאות"""
    DAILY_WINNINGS = "daily_winnings"
    WEEKLY_WINNINGS = "weekly_winnings"
    TOTAL_WINNINGS = "total_winnings"
    REFERRALS = "referrals"
    LEVEL = "level"
    STREAK = "streak"
    GAMES_WON = "games_won"
    HIGHEST_WIN = "highest_win"

class LeaderboardManager:
    """מנהל לוח תוצאות מתקדם"""
    
    def __init__(self):
        self.cache_ttl = 60  # 60 שניות cache
        self.redis_prefix = "leaderboard:"
        self.categories = {
            LeaderboardCategory.DAILY_WINNINGS: {
                "name": "🏅 זכיות יומיות",
                "emoji": "📅",
                "description": "מי זכה בהכי הרבה היום?",
                "score_key": "daily_winnings",
                "reset_hour": 0  // 0 = חצות
            },
            LeaderboardCategory.WEEKLY_WINNINGS: {
                "name": "🏆 זכיות שבועיות",
                "emoji": "📆",
                "description": "מי זכה בהכי הרבה השבוע?",
                "score_key": "weekly_winnings",
                "reset_day": 0  // 0 = יום ראשון
            },
            LeaderboardCategory.TOTAL_WINNINGS: {
                "name": "👑 זכיות כל הזמנים",
                "emoji": "🌟",
                "description": "מי זכה בהכי הרבה בכל הזמנים?",
                "score_key": "total_winnings",
                "permanent": True
            },
            LeaderboardCategory.REFERRALS: {
                "name": "👥 שותפים",
                "emoji": "🤝",
                "description": "מי הזמין הכי הרבה חברים?",
                "score_key": "referrals"
            },
            LeaderboardCategory.STREAK: {
                "name": "🔥 רצף יומי",
                "emoji": "⚡",
                "description": "מי עם הרצף הארוך ביותר?",
                "score_key": "daily_streak"
            },
            LeaderboardCategory.GAMES_WON: {
                "name": "🎮 משחקים שניצחו",
                "emoji": "🏅",
                "description": "מי ניצח בהכי הרבה משחקים?",
                "score_key": "games_won"
            },
            LeaderboardCategory.HIGHEST_WIN: {
                "name": "💰 זכייה הגבוהה ביותר",
                "emoji": "💎",
                "description": "מי עם הזכייה הגבוהה ביותר?",
                "score_key": "highest_win"
            }
        }
        
        self.init_leaderboards()
    
    def init_leaderboards(self):
        """אתחול לוחות תוצאות ב-Redis"""
        for category in self.categories:
            key = self._get_category_key(category)
            if not db.r.exists(key):
                # צור sorted set ריק
                db.r.zadd(key, {"placeholder": 0})
    
    def _get_category_key(self, category: LeaderboardCategory) -> str:
        """קבל מפתח Redis לקטגוריה"""
        return f"{self.redis_prefix}{category.value}"
    
    def _get_daily_key(self, category: LeaderboardCategory) -> str:
        """קבל מפתח יומי לקטגוריה"""
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{self.redis_prefix}daily:{date_str}:{category.value}"
    
    def _get_weekly_key(self, category: LeaderboardCategory) -> str:
        """קבל מפתח שבועי לקטגוריה"""
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        return f"{self.redis_prefix}weekly:{year}_{week_num}:{category.value}"
    
    def _get_cache_key(self, category: LeaderboardCategory, limit: int = 10) -> str:
        """קבל מפתח cache"""
        return f"cache:leaderboard:{category.value}:{limit}"
    
    def update_score(self, user_id: int, score_type: str, amount: int = 1, category: LeaderboardCategory = None):
        """עדכן ניקוד משתמש"""
        if not category:
            # עדכן בכל הקטגוריות הרלוונטיות
            self._update_all_categories(user_id, score_type, amount)
        else:
            self._update_category(user_id, category, amount)
        
        # נקה cache
        self._clear_cache_for_user(user_id)
    
    def _update_all_categories(self, user_id: int, score_type: str, amount: int):
        """עדכן ניקוד בכל הקטגוריות הרלוונטיות"""
        user_key = f"user:{user_id}:profile"
        
        if score_type == "total_winnings":
            # עדכון זכיות כללית
            self._update_category(user_id, LeaderboardCategory.TOTAL_WINNINGS, amount)
            self._update_category(user_id, LeaderboardCategory.DAILY_WINNINGS, amount)
            self._update_category(user_id, LeaderboardCategory.WEEKLY_WINNINGS, amount)
            
            # עדכון זכייה הגבוהה ביותר
            current_high = db.r.hget(user_key, "highest_win") or 0
            if amount > int(current_high):
                db.r.hset(user_key, "highest_win", amount)
                self._update_category(user_id, LeaderboardCategory.HIGHEST_WIN, amount)
        
        elif score_type == "referral":
            self._update_category(user_id, LeaderboardCategory.REFERRALS, amount)
        
        elif score_type == "daily_streak":
            self._update_category(user_id, LeaderboardCategory.STREAK, amount)
        
        elif score_type == "game_win":
            self._update_category(user_id, LeaderboardCategory.GAMES_WON, amount)
    
    def _update_category(self, user_id: int, category: LeaderboardCategory, amount: int):
        """עדכן ניקוד בקטגוריה ספציפית"""
        # מפתח כללי
        category_key = self._get_category_key(category)
        current_score = db.r.zscore(category_key, str(user_id)) or 0
        new_score = float(current_score) + amount
        db.r.zadd(category_key, {str(user_id): new_score})
        
        # מפתח יומי
        daily_key = self._get_daily_key(category)
        current_daily = db.r.zscore(daily_key, str(user_id)) or 0
        db.r.zadd(daily_key, {str(user_id): float(current_daily) + amount})
        db.r.expire(daily_key, 86400)  // 24 שעות
        
        # מפתח שבועי
        weekly_key = self._get_weekly_key(category)
        current_weekly = db.r.zscore(weekly_key, str(user_id)) or 0
        db.r.zadd(weekly_key, {str(user_id): float(current_weekly) + amount})
        db.r.expire(weekly_key, 604800)  // 7 ימים
        
        # שמור ניקוד מקסימלי אם רלוונטי
        if category == LeaderboardCategory.HIGHEST_WIN:
            user_key = f"user:{user_id}:profile"
            current_high = db.r.hget(user_key, "highest_win") or 0
            if amount > int(current_high):
                db.r.hset(user_key, "highest_win", amount)
    
    def get_leaderboard(self, category: LeaderboardCategory, limit: int = 10, use_cache: bool = True) -> List[Dict[str, Any]]:
        """קבל לוח תוצאות לקטגוריה"""
        cache_key = self._get_cache_key(category, limit)
        
        if use_cache:
            cached = db.cache_get(cache_key)
            if cached:
                return cached
        
        leaderboard_key = self._get_category_key(category)
        
        # קבל את ה-top N
        top_users = db.r.zrevrange(leaderboard_key, 0, limit - 1, withscores=True)
        
        results = []
        for rank, (user_id_bytes, score) in enumerate(top_users, 1):
            user_id = int(user_id_bytes.decode() if isinstance(user_id_bytes, bytes) else user_id_bytes)
            
            # דלג על placeholder
            if user_id == 0:
                continue
            
            user_data = db.get_user(user_id)
            if not user_data:
                continue
            
            results.append({
                "rank": rank,
                "user_id": user_id,
                "username": user_data.get("username", ""),
                "first_name": user_data.get("first_name", ""),
                "score": float(score),
                "tier": user_data.get("tier", "Free"),
                "avatar": self._get_avatar_emoji(rank)
            })
        
        # הוסף את המשתמש הנוכחי אם לא נמצא בלוח
        if results and len(results) < limit:
            # ממילא מוגבל ל-top N
            pass
        
        # שמור ב-cache
        if use_cache:
            db.cache_set(cache_key, results, ttl=self.cache_ttl)
        
        return results
    
    def get_user_rank(self, user_id: int, category: LeaderboardCategory) -> Dict[str, Any]:
        """קבל דירוג משתמש בקטגוריה"""
        leaderboard_key = self._get_category_key(category)
        
        # קבל דירוג
        rank = db.r.zrevrank(leaderboard_key, str(user_id))
        score = db.r.zscore(leaderboard_key, str(user_id))
        
        if rank is None or score is None:
            return {
                "rank": None,
                "score": 0,
                "top_percent": 100
            }
        
        rank = rank + 1  // Convert to 1-based ranking
        
        // קבל את מספר המשתתפים הכולל
        total_participants = db.r.zcard(leaderboard_key)
        
        // חשב אחוזון
        if total_participants > 0:
            top_percent = (rank / total_participants) * 100
        else:
            top_percent = 100
        
        return {
            "rank": rank,
            "score": float(score),
            "top_percent": round(top_percent, 1)
        }
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """קבל סטטיסטיקות משתמש מפורטות"""
        user_data = db.get_user(user_id)
        
        if not user_data:
            return {}
        
        stats = {
            "total_winnings": self.get_user_rank(user_id, LeaderboardCategory.TOTAL_WINNINGS),
            "daily_winnings": self.get_user_rank(user_id, LeaderboardCategory.DAILY_WINNINGS),
            "weekly_winnings": self.get_user_rank(user_id, LeaderboardCategory.WEEKLY_WINNINGS),
            "referrals": self.get_user_rank(user_id, LeaderboardCategory.REFERRALS),
            "streak": self.get_user_rank(user_id, LeaderboardCategory.STREAK),
            "games_won": self.get_user_rank(user_id, LeaderboardCategory.GAMES_WON),
            "highest_win": self.get_user_rank(user_id, LeaderboardCategory.HIGHEST_WIN),
            "overall_rank": self._calculate_overall_rank(user_id)
        }
        
        return stats
    
    def _calculate_overall_rank(self, user_id: int) -> Dict[str, Any]:
        """חשב דירוג כללי משוקלל"""
        categories = [
            LeaderboardCategory.TOTAL_WINNINGS,
            LeaderboardCategory.REFERRALS,
            LeaderboardCategory.GAMES_WON,
            LeaderboardCategory.STREAK
        ]
        
        total_score = 0
        max_possible = 0
        
        for category in categories:
            user_rank = self.get_user_rank(user_id, category)
            if user_rank["rank"]:
                // נקודות הפוכות לדירוג (דירוג 1 = 100 נקודות, דירוג 100 = 1 נקודה)
                points = max(0, 101 - user_rank["rank"])
                total_score += points
                max_possible += 100
        
        if max_possible > 0:
            overall_percent = (total_score / max_possible) * 100
        else:
            overall_percent = 0
        
        return {
            "score": total_score,
            "percent": round(overall_percent, 1),
            "medal": self._get_medal_by_percent(overall_percent)
        }
    
    def _get_medal_by_percent(self, percent: float) -> str:
        """קבל מדליה לפי אחוז"""
        if percent >= 90:
            return "🥇"
        elif percent >= 75:
            return "🥈"
        elif percent >= 50:
            return "🥉"
        elif percent >= 25:
            return "🏅"
        else:
            return "🎖️"
    
    def _get_avatar_emoji(self, rank: int) -> str:
        """קבל אמוג'י פרופיל לפי דירוג"""
        if rank == 1:
            return "👑"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        elif rank <= 10:
            return "🌟"
        elif rank <= 50:
            return "⭐"
        else:
            return "👤"
    
    def _clear_cache_for_user(self, user_id: int):
        """נקה cache עבור משתמש"""
        for category in self.categories:
            for limit in [10, 25, 50]:
                cache_key = self._get_cache_key(category, limit)
                db.cache_delete(cache_key)
    
    def reset_daily_leaderboards(self):
        """אפס לוחות תוצאות יומיים"""
        now = datetime.now()
        
        for category in self.categories:
            category_config = self.categories[category]
            
            if "reset_hour" in category_config:
                if now.hour == category_config["reset_hour"]:
                    daily_key = self._get_daily_key(category)
                    db.r.delete(daily_key)
    
    def reset_weekly_leaderboards(self):
        """אפס לוחות תוצאות שבועיים"""
        now = datetime.now()
        
        for category in self.categories:
            category_config = self.categories[category]
            
            if "reset_day" in category_config:
                if now.weekday() == category_config["reset_day"]:
                    weekly_key = self._get_weekly_key(category)
                    db.r.delete(weekly_key)

# ============ ANIMATED LEADERBOARD DISPLAY ============
class AnimatedLeaderboardDisplay:
    """הצגת לוח תוצאות עם אנימציות"""
    
    @staticmethod
    async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               category: LeaderboardCategory = LeaderboardCategory.TOTAL_WINNINGS):
        """הצג לוח תוצאות עם אנימציות"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        // אנימציית טעינה
        await AnimatedLeaderboardDisplay._show_loading_animation(query)
        
        // קבל נתונים
        leaderboard = leaderboard_manager.get_leaderboard(category, limit=15)
        category_config = leaderboard_manager.categories[category]
        
        // צור טקסט לוח תוצאות
        leaderboard_text = AnimatedLeaderboardDisplay._create_leaderboard_text(
            leaderboard, category_config, user_id
        )
        
        // צור מקלדת בחירת קטגוריה
        keyboard = AnimatedLeaderboardDisplay._create_category_keyboard(category, user_id)
        
        // הצג עם אנימציה
        await AnimatedLeaderboardDisplay._display_with_animation(
            query, leaderboard_text, keyboard
        )
    
    @staticmethod
    async def _show_loading_animation(query):
        """אנימציית טעינה"""
        loading_frames = ["🏆", "🎮", "💰", "👑", "🌟", "⚡", "🔥"]
        
        for frame in loading_frames:
            try:
                await query.edit_message_text(f"{frame} טוען לוח תוצאות...")
                await asyncio.sleep(0.2)
            except:
                break
    
    @staticmethod
    def _create_leaderboard_text(leaderboard: List[Dict], category_config: Dict, current_user_id: int) -> str:
        """צור טקסט לוח תוצאות מפורט"""
        category_emoji = category_config["emoji"]
        category_name = category_config["name"]
        description = category_config["description"]
        
        text = f"{category_emoji} **{category_name}**\n"
        text += f"_{description}_\n\n"
        
        if not leaderboard:
            text += "📭 עדיין אין נתונים בלוח התוצאות...\nהפוך לשחקן הראשון! 🎮"
            return text
        
        // הוסף את 10 המובילים
        for i, entry in enumerate(leaderboard[:10], 1):
            rank = entry["rank"]
            avatar = entry["avatar"]
            first_name = entry["first_name"]
            username = entry["username"]
            score = entry["score"]
            tier = entry["tier"]
            
            // עיצוב שם משתמש
            display_name = first_name
            if username:
                display_name = f"@{username}"
            
            // עיצוב ניקוד
            formatted_score = AnimatedLeaderboardDisplay._format_score(score, category_config["score_key"])
            
            // קו דירוג
            rank_line = f"{avatar} **{rank}.** {display_name}"
            
            // הוסף סמל דרגה
            if tier == "VIP":
                rank_line += " 👑"
            elif tier == "Pro":
                rank_line += " ⚡"
            
            rank_line += f" ➜ {formatted_score}\n"
            
            text += rank_line
        
        // הוסף קו מפריד
        text += "\n" + "─" * 30 + "\n\n"
        
        // הוסף את דירוג המשתמש הנוכחי
        user_rank = leaderboard_manager.get_user_rank(current_user_id, 
                                                     LeaderboardCategory(category_config["score_key"]))
        
        if user_rank["rank"]:
            user_data = db.get_user(current_user_id)
            tier = user_data.get("tier", "Free")
            tier_emoji = "👑" if tier == "VIP" else "⚡" if tier == "Pro" else "👤"
            
            text += f"**הדירוג שלך:**\n"
            text += f"{tier_emoji} **מקום {user_rank['rank']:,}** "
            text += f"(Top {user_rank['top_percent']}%)\n"
            text += f"📊 **ניקוד:** {AnimatedLeaderboardDisplay._format_score(user_rank['score'], category_config['score_key'])}\n"
        
        // הוסף זמן עדכון
        update_time = datetime.now().strftime("%H:%M")
        text += f"\n_🕐 עודכן: {update_time}_"
        
        return text
    
    @staticmethod
    def _format_score(score: float, score_key: str) -> str:
        """עצב ניקוד לפי סוג"""
        if score_key in ["daily_winnings", "weekly_winnings", "total_winnings", "highest_win"]:
            if score >= 1_000_000:
                return f"{score/1_000_000:.1f}M 🪙"
            elif score >= 1_000:
                return f"{score/1_000:.1f}K 🪙"
            else:
                return f"{int(score):,} 🪙"
        elif score_key == "referrals":
            return f"{int(score):,} 👥"
        elif score_key == "daily_streak":
            return f"{int(score)} ימים 🔥"
        elif score_key == "games_won":
            return f"{int(score):,} 🎮"
        else:
            return f"{int(score):,}"
    
    @staticmethod
    def _create_category_keyboard(current_category: LeaderboardCategory, user_id: int) -> InlineKeyboardMarkup:
        """צור מקלדת בחירת קטגוריה"""
        categories = [
            (LeaderboardCategory.TOTAL_WINNINGS, "👑 כל הזמנים"),
            (LeaderboardCategory.DAILY_WINNINGS, "📅 יומי"),
            (LeaderboardCategory.WEEKLY_WINNINGS, "📆 שבועי"),
            (LeaderboardCategory.REFERRALS, "👥 שותפים"),
            (LeaderboardCategory.STREAK, "🔥 רצף"),
            (LeaderboardCategory.GAMES_WON, "🎮 ניצחונות")
        ]
        
        keyboard = []
        row = []
        
        for category, label in categories:
            callback = f"leaderboard_{category.value}"
            is_active = category == current_category
            
            if is_active:
                label = f"• {label} •"
            
            row.append(InlineKeyboardButton(label, callback_data=callback))
            
            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        // כפתורים נוספים
        keyboard.append([
            InlineKeyboardButton("📊 הסטטיסטיקות שלי", callback_data="my_stats"),
            InlineKeyboardButton("🔄 רענן", callback_data=f"leaderboard_{current_category.value}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start"),
            InlineKeyboardButton("🎮 חזרה למשחקים", callback_data="game_select")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    async def _display_with_animation(query, text: str, keyboard: InlineKeyboardMarkup):
        """הצג עם אנימציה הדרגתית"""
        # פיצול הטקסט לשורות
        lines = text.split('\n')
        displayed_text = ""
        
        for i, line in enumerate(lines):
            displayed_text += line + "\n"
            
            // הצג כל 3 שורות עם השהייה קטנה
            if i % 3 == 0 or i == len(lines) - 1:
                try:
                    await query.edit_message_text(
                        text=displayed_text + "▌" if i < len(lines) - 1 else displayed_text,
                        reply_markup=keyboard if i == len(lines) - 1 else None,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(0.05)
                except:
                    pass
        
        // הסר את סמן הסיום
        try:
            await query.edit_message_text(
                text=displayed_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass

# ============ USER STATS DISPLAY ============
async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """הצג סטטיסטיקות משתמש מפורטות"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    // אנימציית טעינה
    loading_frames = ["📊", "📈", "📉", "🎯", "⚡", "🔥"]
    for frame in loading_frames:
        try:
            await query.edit_message_text(f"{frame} אוסף נתונים...")
            await asyncio.sleep(0.2)
        except:
            break
    
    // קבל נתונים
    user_data = db.get_user(user_id)
    stats = leaderboard_manager.get_user_stats(user_id)
    
    // צור טקסט סטטיסטיקות
    stats_text = await create_stats_display(user_id, user_data, stats)
    
    // מקלדת
    keyboard = [
        [InlineKeyboardButton("🏆 לוח תוצאות", callback_data="leaderboard_total_winnings"),
         InlineKeyboardButton("🔄 רענן", callback_data="my_stats")],
        [InlineKeyboardButton("📈 גרפים", callback_data="stats_graphs"),
         InlineKeyboardButton("🎮 משחקים", callback_data="game_select")],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def create_stats_display(user_id: int, user_data: Dict, stats: Dict) -> str:
    """צור תצוגת סטטיסטיקות מפורטת"""
    if not user_data:
        return "❌ לא נמצאו נתונים"
    
    // מידע בסיסי
    first_name = user_data.get("first_name", "שחקן")
    username = user_data.get("username", "")
    tier = user_data.get("tier", "Free")
    balance = int(user_data.get("balance", 0))
    joined = user_data.get("joined", "")
    
    // עיצוב תאריך הצטרפות
    if joined:
        try:
            join_date = datetime.fromisoformat(joined)
            days_since = (datetime.now() - join_date).days
            join_text = f"{days_since} ימים"
        except:
            join_text = joined
    else:
        join_text = "לאחרונה"
    
    // אמוג'י דרגה
    tier_emoji = {"Free": "🆓", "Pro": "⚡", "VIP": "👑"}.get(tier, "👤")
    
    // התחלת טקסט
    text = f"👤 **פרופיל שחקן**\n\n"
    text += f"{tier_emoji} **{first_name}**"
    if username:
        text += f" (@{username})\n"
    else:
        text += "\n"
    
    text += f"💎 **דרגה:** {tier}\n"
    text += f"💰 **יתרה:** {balance:,} 🪙\n"
    text += f"📅 **חבר:** לפני {join_text}\n"
    
    text += "\n" + "📊 " + "סטטיסטיקות משחק" + "\n" + "─" * 30 + "\n\n"
    
    // סטטיסטיקות דירוג
    if stats:
        overall = stats.get("overall_rank", {})
        if overall.get("percent", 0) > 0:
            text += f"🏆 **דירוג כללי:** {overall['medal']} Top {overall['percent']}%\n"
        
        // דירוגים ספציפיים
        ranking_fields = [
            ("total_winnings", "👑 זכיות כל הזמנים"),
            ("daily_winnings", "📅 זכיות יומיות"),
            ("weekly_winnings", "📆 זכיות שבועיות"),
            ("referrals", "👥 הפניות"),
            ("streak", "🔥 רצף יומי"),
            ("games_won", "🎮 משחקים שניצחו"),
            ("highest_win", "💰 זכייה גבוהה ביותר")
        ]
        
        for field_key, field_name in ranking_fields:
            if field_key in stats:
                rank_data = stats[field_key]
                if rank_data.get("rank"):
                    score_text = leaderboard_manager._format_score(
                        rank_data["score"], 
                        field_key
                    )
                    text += f"{field_name}: מקום {rank_data['rank']:,} ({score_text})\n"
        
        // הישגים מיוחדים
        text += "\n" + "🎖️ " + "הישגים מיוחדים" + "\n" + "─" * 30 + "\n"
        
        achievements = []
        
        if stats.get("highest_win", {}).get("score", 0) >= 1000:
            achievements.append("💰 טייקון (זכייה של 1,000+ מטבעות)")
        
        if stats.get("referrals", {}).get("score", 0) >= 10:
            achievements.append("👥 סלבס (10+ הפניות)")
        
        if stats.get("streak", {}).get("score", 0) >= 7:
            achievements.append("🔥 מחויב (רצף של 7+ ימים)")
        
        if stats.get("games_won", {}).get("score", 0) >= 50:
            achievements.append("🎮 אלוף (50+ ניצחונות)")
        
        if achievements:
            for ach in achievements:
                text += f"• {ach}\n"
        else:
            text += "עדיין אין הישגים מיוחדים. המשך לשחק! 🎮\n"
    
    // טיפים לשיפור
    text += "\n" + "💡 " + "טיפים לשיפור" + "\n" + "─" * 30 + "\n"
    
    tips = [
        "🎯 שחק מדי יום כדי לשמור על רצף",
        "👥 הזמן חברים לקבלת בונוסים",
        "💎 שדרג ל-VIP לקבלת מכפילים גבוהים יותר",
        "📊 עקוב אחר הלוח תוצאות כדי לראות את המיקום שלך"
    ]
    
    for tip in tips:
        text += f"• {tip}\n"
    
    // זמן עדכון
    update_time = datetime.now().strftime("%H:%M")
    text += f"\n_🕐 עודכן: {update_time}_"
    
    return text

# ============ LEADERBOARD HANDLERS ============
async def handle_leaderboard_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בבחירת קטגוריה בלוח תוצאות"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "my_stats":
        await show_user_stats(update, context)
        return
    
    if data.startswith("leaderboard_"):
        category_str = data.replace("leaderboard_", "")
        
        try:
            category = LeaderboardCategory(category_str)
            await AnimatedLeaderboardDisplay.show_leaderboard(update, context, category)
        except ValueError:
            // ברירת מחדל
            await AnimatedLeaderboardDisplay.show_leaderboard(update, context)

# ============ AUTO-RESET TASK ============
async def auto_reset_leaderboards():
    """משימה אוטומטית לאיפוס לוחות תוצאות"""
    while True:
        try:
            now = datetime.now()
            
            // בדוק אם חצות (איפוס יומי)
            if now.hour == 0 and now.minute == 0:
                leaderboard_manager.reset_daily_leaderboards()
                print("✅ אופסו לוחות תוצאות יומיים")
            
            // בדוק אם יום ראשון 00:00 (איפוס שבועי)
            if now.weekday() == 6 and now.hour == 0 and now.minute == 0:
                leaderboard_manager.reset_weekly_leaderboards()
                print("✅ אופסו לוחות תוצאות שבועיים")
            
            // המתן לדקה הבאה
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"❌ שגיאה באיפוס לוחות תוצאות: {e}")
            await asyncio.sleep(60)

# ============ INITIALIZATION ============
leaderboard_manager = LeaderboardManager()

def register_leaderboard_handlers(application):
    """רישום מטפלים ללוח תוצאות"""
    application.add_handler(CallbackQueryHandler(handle_leaderboard_selection, pattern="^leaderboard_"))
    application.add_handler(CallbackQueryHandler(show_user_stats, pattern="^my_stats$"))
    application.add_handler(CallbackQueryHandler(show_user_stats, pattern="^stats_graphs$"))

# הפעל משימת איפוס אוטומטית
def start_auto_reset_task():
    """הפעל את משימת האיפוס האוטומטית"""
    import threading
    thread = threading.Thread(target=lambda: asyncio.run(auto_reset_leaderboards()), daemon=True)
    thread.start()

if __name__ == "__main__":
    print("🏆 מודול לוח תוצאות נטען בהצלחה")
    
    // בדיקות
    test_user_id = 12345
    leaderboard_manager.update_score(test_user_id, "total_winnings", 1000)
    
    leaderboard = leaderboard_manager.get_leaderboard(LeaderboardCategory.TOTAL_WINNINGS)
    print(f"📊 לוח תוצאות: {len(leaderboard)} משתתפים")
    
    user_rank = leaderboard_manager.get_user_rank(test_user_id, LeaderboardCategory.TOTAL_WINNINGS)
    print(f"👤 דירוג משתמש: {user_rank}")
    
    print("✅ כל הבדיקות עברו בהצלחה!")
