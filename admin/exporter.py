import pandas as pd
from datetime import datetime
from app.database.manager import db

def export_users_to_excel():
    """Export all users to Excel file"""
    users = db.r.smembers("users:total")
    
    data = []
    for user_id in users:
        user_data = db.get_user(user_id)
        if user_data:
            data.append({
                'ID': user_id,
                'Username': user_data.get('username', ''),
                'First Name': user_data.get('first_name', ''),
                'Balance': user_data.get('balance', 0),
                'Tier': user_data.get('tier', 'Free'),
                'Joined': user_data.get('joined', ''),
                'Referrer': user_data.get('referrer', '')
            })
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'users_export_{timestamp}.xlsx'
    
    # Save to Excel
    df.to_excel(filename, index=False)
    
    return filename
