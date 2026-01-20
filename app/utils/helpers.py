def format_number(num):
    """Format number with commas"""
    return f"{num:,}"

def validate_user_input(text, max_length=100):
    """Validate user input"""
    if not text or len(text) > max_length:
        return False
    # Add more validation as needed
    return True

def calculate_commission(amount, percentage):
    """Calculate commission"""
    return (amount * percentage) / 100
