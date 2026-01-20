"""
🎨 NFTY ULTRA PRO - Theme System
מערכת עיצוב מתקדמת עם אנימציות, סגנונות, ואפקטים ויזואליים
"""

import random
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

class ThemeType(Enum):
    """סוגי עיצוב זמינים"""
    DEFAULT = "default"
    DARK = "dark"
    NEON = "neon"
    LUXURY = "luxury"
    RETRO = "retro"
    FUTURISTIC = "futuristic"

class AnimationType(Enum):
    """סוגי אנימציות"""
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    BOUNCE = "bounce"
    SPIN = "spin"
    FLASH = "flash"
    PULSE = "pulse"
    RAINBOW = "rainbow"

class ThemeManager:
    """מנהל עיצוב ואנימציות"""
    
    # הגדרות עיצוב לכל סוג
    THEME_CONFIGS = {
        ThemeType.DEFAULT: {
            "name": "ברירת מחדל",
            "emoji": "🎨",
            "colors": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "background": "#ecf0f1",
                "text": "#2c3e50"
            },
            "emojis": {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
                "coin": "🪙",
                "diamond": "💎",
                "trophy": "🏆"
            }
        },
        ThemeType.DARK: {
            "name": "כהה",
            "emoji": "🌙",
            "colors": {
                "primary": "#1a1a2e",
                "secondary": "#16213e",
                "accent": "#0f3460",
                "background": "#222831",
                "text": "#eeeeee"
            },
            "emojis": {
                "success": "🟢",
                "error": "🔴",
                "warning": "🟡",
                "info": "🔵",
                "coin": "💰",
                "diamond": "💠",
                "trophy": "🎯"
            }
        },
        ThemeType.NEON: {
            "name": "נאון",
            "emoji": "🌃",
            "colors": {
                "primary": "#00ff9d",
                "secondary": "#00b8ff",
                "accent": "#ff00ff",
                "background": "#0a0a0a",
                "text": "#ffffff"
            },
            "emojis": {
                "success": "✨",
                "error": "💥",
                "warning": "⚡",
                "info": "🔆",
                "coin": "🌟",
                "diamond": "💫",
                "trophy": "🚀"
            }
        },
        ThemeType.LUXURY: {
            "name": "יוקרה",
            "emoji": "👑",
            "colors": {
                "primary": "#d4af37",
                "secondary": "#c0c0c0",
                "accent": "#b8860b",
                "background": "#1a1a1a",
                "text": "#f8f8ff"
            },
            "emojis": {
                "success": "👑",
                "error": "💔",
                "warning": "💎",
                "info": "🔱",
                "coin": "🪙",
                "diamond": "💍",
                "trophy": "🏆"
            }
        },
        ThemeType.RETRO: {
            "name": "רטרו",
            "emoji": "📺",
            "colors": {
                "primary": "#ff6b6b",
                "secondary": "#4ecdc4",
                "accent": "#ffd166",
                "background": "#1a535c",
                "text": "#f7fff7"
            },
            "emojis": {
                "success": "🕹️",
                "error": "📛",
                "warning": "🔶",
                "info": "📺",
                "coin": "🪙",
                "diamond": "💠",
                "trophy": "🏅"
            }
        },
        ThemeType.FUTURISTIC: {
            "name":עתידני",
            "emoji": "🚀",
            "colors": {
                "primary": "#00d4ff",
                "secondary": "#0099ff",
                "accent": "#ff00cc",
                "background": "#000033",
                "text": "#ffffff"
            },
            "emojis": {
                "success": "🤖",
                "error": "👾",
                "warning": "🛸",
                "info": "⚡",
                "coin": "🔷",
                "diamond": "💠",
                "trophy": "🏆"
            }
        }
    }
    
    # הגדרות אנימציה
    ANIMATION_CONFIGS = {
        AnimationType.FADE: {
            "name": "היעלמות",
            "frames": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"]
        },
        AnimationType.SLIDE: {
            "name": "החלקה",
            "frames": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
        },
        AnimationType.ZOOM: {
            "name": "זום",
            "frames": ["○", "◎", "●", "◉", "●", "◎", "○"]
        },
        AnimationType.BOUNCE: {
            "name": "קפיצה",
            "frames": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"]
        },
        AnimationType.SPIN: {
            "name": "סיבוב",
            "frames": ["◐", "◓", "◑", "◒"]
        },
        AnimationType.FLASH: {
            "name": "הבהוב",
            "frames": ["█", "░", "█", "▒", "█", "▓", "█"]
        },
        AnimationType.PULSE: {
            "name": "דופק",
            "frames": ["○", "⭕", "◎", "⭕", "○"]
        },
        AnimationType.RAINBOW: {
            "name": "קשת",
            "frames": ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
        }
    }
    
    @staticmethod
    def get_theme(theme_type: ThemeType = ThemeType.DEFAULT) -> Dict[str, Any]:
        """קבל הגדרות עיצוב"""
        return ThemeManager.THEME_CONFIGS.get(theme_type, ThemeManager.THEME_CONFIGS[ThemeType.DEFAULT])
    
    @staticmethod
    def get_animation(animation_type: AnimationType = AnimationType.FADE) -> Dict[str, Any]:
        """קבל הגדרות אנימציה"""
        return ThemeManager.ANIMATION_CONFIGS.get(animation_type, ThemeManager.ANIMATION_CONFIGS[AnimationType.FADE])
    
    @staticmethod
    def apply_theme_to_text(text: str, theme: ThemeType = ThemeType.DEFAULT, animation: AnimationType = None) -> str:
        """החל עיצוב ואנימציות על טקסט"""
        theme_config = ThemeManager.get_theme(theme)
        
        # הוסף אנימציה אם מתבקש
        if animation:
            animation_config = ThemeManager.get_animation(animation)
            frames = animation_config.get("frames", [])
            if frames:
                text = f"{frames[0]} {text}"
        
        # הוסף אמוג'י נושא אם יש
        emoji = theme_config.get("emoji", "")
        if emoji:
            text = f"{emoji} {text}"
        
        return text
    
    @staticmethod
    def create_themed_keyboard(buttons: List[List[Dict]], theme: ThemeType = ThemeType.DEFAULT) -> InlineKeyboardMarkup:
        """צור מקלדת עם עיצוב תואם"""
        theme_config = ThemeManager.get_theme(theme)
        emojis = theme_config.get("emojis", {})
        
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                text = button.get("text", "")
                callback = button.get("callback", "")
                
                # הוסף אמוג'י לפי סוג הכפתור
                if "start" in callback.lower() or "play" in callback.lower():
                    text = f"🎮 {text}"
                elif "shop" in callback.lower() or "buy" in callback.lower():
                    text = f"🛒 {text}"
                elif "stats" in callback.lower() or "report" in callback.lower():
                    text = f"📊 {text}"
                elif "help" in callback.lower() or "guide" in callback.lower():
                    text = f"❓ {text}"
                elif "back" in callback.lower() or "return" in callback.lower():
                    text = f"🔙 {text}"
                elif "close" in callback.lower() or "exit" in callback.lower():
                    text = f"❌ {text}"
                
                keyboard_row.append(InlineKeyboardButton(text, callback_data=callback))
            keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_balance(balance: int, theme: ThemeType = ThemeType.DEFAULT) -> str:
        """עצב יתרה עם עיצוב"""
        theme_config = ThemeManager.get_theme(theme)
        emojis = theme_config.get("emojis", {})
        coin_emoji = emojis.get("coin", "🪙")
        
        if balance >= 1000000:
            formatted = f"{balance/1000000:.1f}M"
        elif balance >= 1000:
            formatted = f"{balance/1000:.1f}K"
        else:
            formatted = str(balance)
        
        return f"{coin_emoji} {formatted}"
    
    @staticmethod
    def format_tier(tier: str, theme: ThemeType = ThemeType.DEFAULT) -> str:
        """עצב דרגה עם עיצוב"""
        tier_emojis = {
            "Free": "🆓",
            "Pro": "⚡",
            "VIP": "👑"
        }
        
        emoji = tier_emojis.get(tier, "👤")
        return f"{emoji} {tier}"

class AnimatedMessage:
    """הודעות עם אנימציות"""
    
    def __init__(self, theme: ThemeType = ThemeType.DEFAULT):
        self.theme = theme
        self.theme_config = ThemeManager.get_theme(theme)
    
    async def send_loading(self, query, message: str = "טוען...") -> None:
        """שלח הודעת טעינה עם אנימציה"""
        frames = ["⏳", "⌛", "⏳", "⏰", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
        
        for frame in frames:
            try:
                await query.edit_message_text(f"{frame} {message}")
                await asyncio.sleep(0.2)
            except:
                break
    
    async def send_success(self, query, message: str) -> None:
        """שלח הודעת הצלחה עם אנימציה"""
        emoji = self.theme_config["emojis"]["success"]
        frames = [f"{emoji} {message}", f"✨ {message}", f"🎉 {message}", f"✅ {message}"]
        
        for frame in frames:
            try:
                await query.edit_message_text(frame)
                await asyncio.sleep(0.3)
            except:
                break
    
    async def send_error(self, query, message: str) -> None:
        """שלח הודעת שגיאה עם אנימציה"""
        emoji = self.theme_config["emojis"]["error"]
        frames = [f"{emoji} {message}", f"💥 {message}", f"❌ {message}", f"⚠️ {message}"]
        
        for frame in frames:
            try:
                await query.edit_message_text(frame)
                await asyncio.sleep(0.3)
            except:
                break
    
    async def countdown(self, query, from_num: int = 3, message: str = "מתחיל") -> None:
        """אנימציית ספירה לאחור"""
        for i in range(from_num, 0, -1):
            try:
                await query.edit_message_text(f"{message}... {i} ⏱️")
                await asyncio.sleep(1)
            except:
                break

class ParticleEffect:
    """אפקטים חלקיקיים לאנימציות מתקדמות"""
    
    @staticmethod
    async def create_explosion(query, duration: float = 1.0) -> None:
        """אפקט פיצוץ"""
        explosion_frames = [
            "💣", "💥", "🔥", "☠️", "💀", "👻",
            "💨", "🌪️", "🌀", "⚡", "✨"
        ]
        
        for frame in explosion_frames:
            try:
                await query.edit_message_text(f"{frame}")
                await asyncio.sleep(duration / len(explosion_frames))
            except:
                pass
    
    @staticmethod
    async def create_fireworks(query, duration: float = 1.5) -> None:
        """אפקט זיקוקים"""
        fireworks = ["🎆", "🎇", "✨", "🎉", "🎊", "🏆"]
        
        for firework in fireworks:
            try:
                await query.edit_message_text(f"{firework}")
                await asyncio.sleep(duration / len(fireworks))
            except:
                pass
    
    @staticmethod
    async def create_rain(query, duration: float = 1.0) -> None:
        """אפקט גשם מטבעות"""
        coins = ["🪙", "💰", "💵", "💸", "💎", "💍", "👑"]
        
        for coin in coins:
            try:
                await query.edit_message_text(f"{coin}")
                await asyncio.sleep(duration / len(coins))
            except:
                pass

# פונקציות עזר מהירות
def get_theme(theme_name: str = "default") -> ThemeType:
    """קבל סוג עיצוב מסטרינג"""
    theme_map = {
        "default": ThemeType.DEFAULT,
        "dark": ThemeType.DARK,
        "neon": ThemeType.NEON,
        "luxury": ThemeType.LUXURY,
        "retro": ThemeType.RETRO,
        "futuristic": ThemeType.FUTURISTIC
    }
    return theme_map.get(theme_name.lower(), ThemeType.DEFAULT)

def apply_theme(text: str, theme_name: str = "default") -> str:
    """החל עיצוב על טקסט (קיצור)"""
    theme = get_theme(theme_name)
    return ThemeManager.apply_theme_to_text(text, theme)

def create_animated_loading(task_name: str = "") -> str:
    """צור אינדיקטור טעינה אנימטיבי"""
    loaders = ["⏳", "⌛", "⏰", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
    loader = random.choice(loaders)
    
    if task_name:
        return f"{loader} {task_name}..."
    return f"{loader} טוען..."

# יצירת מופעים גלובליים
theme_manager = ThemeManager()
animated_message = AnimatedMessage()
particle_effect = ParticleEffect()

if __name__ == "__main__":
    print("🧪 בדיקת מערכת העיצוב...")
    
    # בדיקת עיצובים
    for theme in ThemeType:
        config = theme_manager.get_theme(theme)
        print(f"🎨 {theme.value}: {config['name']} {config['emoji']}")
    
    print("\n🎭 בדיקת אנימציות:")
    for anim in AnimationType:
        config = theme_manager.get_animation(anim)
        print(f"  {anim.value}: {config['name']}")
    
    print("\n✅ מערכת העיצוב פועלת כשורה!")
