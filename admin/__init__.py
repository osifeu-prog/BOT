# admin/__init__.py
from .dashboard import (
    send_admin_report,
    broadcast,
    broadcast_confirmed,
    admin_stats_realtime,
    generate_user_growth_chart
)

# רישום handlers ב-Main.py
def setup_admin_handlers(application):
    """Setup all admin handlers"""
    from .dashboard import (
        send_admin_report,
        broadcast,
        broadcast_confirmed,
        admin_stats_realtime
    )
    
    # Command handlers
    application.add_handler(CommandHandler("stats", admin_stats_realtime))
    application.add_handler(CommandHandler("report", send_admin_report))
    application.add_handler(CommandHandler("broadcast", broadcast))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(
        broadcast_confirmed, 
        pattern="^broadcast_confirm_"
    ))
    application.add_handler(CallbackQueryHandler(
        admin_stats_realtime, 
        pattern="^refresh_stats$"
    ))
