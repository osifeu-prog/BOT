# ב-database/manager.py
class DatabaseManager:
    # ... קוד קיים ...
    
    def get_daily_stats(self, date=None):
        """Get daily statistics"""
        if date is None:
            date = datetime.now().date()
        
        return {
            "games": self.get_games_count(date),
            "transactions": self.get_transactions_count(date),
            "revenue": self.get_revenue(date),
            "new_users": self.get_new_users(date)
        }
    
    def get_signups_by_date(self, date):
        """Get number of signups on specific date"""
        # לוגיקה לפי המבנה שלך
        pass
    
    def get_active_users(self, hours=24):
        """Get count of active users in last X hours"""
        pass
