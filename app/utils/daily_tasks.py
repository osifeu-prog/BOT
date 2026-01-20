# app/utils/daily_tasks.py
from datetime import datetime, timedelta
from app.database.manager import db
import json

class DailyTasksSystem:
    def __init__(self):
        self.tasks = {
            'daily_login': {
                'name': 'כניסה יומית',
                'reward': 100,
                'description': 'היכנס לבוט כל יום'
            },
            'play_3_games': {
                'name': 'שחק 3 משחקים',
                'reward': 250,
                'description': 'שחק 3 משחקים שונים'
            },
            'invite_friend': {
                'name': 'הזמן חבר',
                'reward': 500,
                'description': 'הזמן חבר חדש'
            },
            'win_game': {
                'name': 'נצח במשחק',
                'reward': 300,
                'description': 'נצח במשחק כלשהו'
            },
            'vip_upgrade': {
                'name': 'שדרג ל-VIP',
                'reward': 1000,
                'description': 'עלה לדרגת VIP'
            }
        }
    
    def get_daily_tasks(self, user_id):
        """קבל את המשימות היומיות למשתמש"""
        today = datetime.now().strftime('%Y-%m-%d')
        tasks_key = f"user:{user_id}:daily_tasks:{today}"
        
        # אם אין משימות להיום, צור חדשות
        if not db.r.exists(tasks_key):
            daily_tasks = {}
            for task_id, task_info in self.tasks.items():
                daily_tasks[task_id] = {
                    **task_info,
                    'completed': False,
                    'claimed': False,
                    'progress': 0,
                    'max_progress': 1
                }
            
            # התאם התקדמות למשימות מיוחדות
            daily_tasks['play_3_games']['max_progress'] = 3
            daily_tasks['play_3_games']['progress'] = 0
            
            db.r.setex(tasks_key, 86400, json.dumps(daily_tasks))
        else:
            daily_tasks = json.loads(db.r.get(tasks_key))
        
        return daily_tasks
    
    def update_task_progress(self, user_id, task_id, progress=1):
        """עדכן התקדמות במשימה"""
        today = datetime.now().strftime('%Y-%m-%d')
        tasks_key = f"user:{user_id}:daily_tasks:{today}"
        
        if db.r.exists(tasks_key):
            tasks = json.loads(db.r.get(tasks_key))
            
            if task_id in tasks:
                if not tasks[task_id]['completed']:
                    tasks[task_id]['progress'] += progress
                    
                    # בדוק אם המשימה הושלמה
                    if tasks[task_id]['progress'] >= tasks[task_id]['max_progress']:
                        tasks[task_id]['completed'] = True
                    
                    db.r.setex(tasks_key, 86400, json.dumps(tasks))
                    return True
        
        return False
    
    def claim_task_reward(self, user_id, task_id):
        """קבל פרס על משימה שהושלמה"""
        today = datetime.now().strftime('%Y-%m-%d')
        tasks_key = f"user:{user_id}:daily_tasks:{today}"
        
        if db.r.exists(tasks_key):
            tasks = json.loads(db.r.get(tasks_key))
            
            if task_id in tasks and tasks[task_id]['completed'] and not tasks[task_id]['claimed']:
                reward = tasks[task_id]['reward']
                
                # תן את הפרס
                db.r.hincrby(f"user:{user_id}:profile", "balance", reward)
                tasks[task_id]['claimed'] = True
                
                db.r.setex(tasks_key, 86400, json.dumps(tasks))
                
                # רשום את העסקה
                db.log_transaction(user_id, reward, f"Daily task: {tasks[task_id]['name']}")
                
                return reward
        
        return 0

daily_tasks = DailyTasksSystem()
