import logging
import json
from logging.handlers import RotatingFileHandler

class BotLogger:
    def __init__(self, name="nfty_bot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            "bot_logs.json",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_game(self, user_id, game_name, bet, win, result):
        self.logger.info(
            f"Game played: {game_name}, Bet: {bet}, Win: {win}, Result: {result}",
            extra={"user": user_id}
        )
    
    def log_transaction(self, user_id, tx_type, amount, details=""):
        self.logger.info(
            f"Transaction: {tx_type}, Amount: {amount}, Details: {details}",
            extra={"user": user_id}
        )
    
    def log_error(self, user_id, error_msg, traceback=""):
        self.logger.error(
            f"Error: {error_msg}, Traceback: {traceback}",
            extra={"user": user_id}
        )

# Global instance
logger = BotLogger()
