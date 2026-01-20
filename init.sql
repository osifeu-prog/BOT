-- 🎰 NFTY ULTRA PRO - Database Schema
-- סכמת מסד נתונים מתקדמת לסטטיסטיקות ונתוני משתמשים ארוכי טווח

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (משתמשים)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    tier VARCHAR(50) DEFAULT 'Free',
    balance BIGINT DEFAULT 100,
    referral_code VARCHAR(50) UNIQUE,
    referrer_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Games table (משחקים)
CREATE TABLE games (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    game_type VARCHAR(50) NOT NULL,
    bet_amount BIGINT NOT NULL,
    win_amount BIGINT,
    result VARCHAR(50),
    multiplier DECIMAL(5,2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Transactions table (עסקאות)
CREATE TABLE transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- deposit, withdrawal, win, loss, bonus, referral
    amount BIGINT NOT NULL,
    balance_before BIGINT,
    balance_after BIGINT,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Referrals table (הפניות)
CREATE TABLE referrals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    referrer_id BIGINT REFERENCES users(id),
    referred_id BIGINT REFERENCES users(id) UNIQUE,
    reward_amount BIGINT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- VIP Purchases table (רכישות VIP)
CREATE TABLE vip_purchases (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    tier VARCHAR(50) NOT NULL,
    amount_paid DECIMAL(10,2),
    currency VARCHAR(10),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Daily Tasks table (משימות יומיות)
CREATE TABLE daily_tasks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    date DATE NOT NULL,
    tasks_completed JSONB DEFAULT '{}',
    streak_days INTEGER DEFAULT 0,
    total_rewards BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Leaderboard table (לוח תוצאות)
CREATE TABLE leaderboards (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    period VARCHAR(50) NOT NULL, -- daily, weekly, monthly, all_time
    category VARCHAR(50) NOT NULL, -- winnings, referrals, games_played
    user_id BIGINT REFERENCES users(id),
    score BIGINT NOT NULL,
    rank INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period, category, user_id)
);

-- Analytics table (אנליטיקס)
CREATE TABLE analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id BIGINT REFERENCES users(id),
    properties JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table (התראות)
CREATE TABLE notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Audit Log table (יומן פעולות)
CREATE TABLE audit_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    changes JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_tier ON users(tier);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_games_user_id ON games(user_id);
CREATE INDEX idx_games_game_type ON games(game_type);
CREATE INDEX idx_games_created_at ON games(created_at);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

CREATE INDEX idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX idx_referrals_referred_id ON referrals(referred_id);
CREATE INDEX idx_referrals_status ON referrals(status);

CREATE INDEX idx_vip_purchases_user_id ON vip_purchases(user_id);
CREATE INDEX idx_vip_purchases_status ON vip_purchases(status);
CREATE INDEX idx_vip_purchases_expires_at ON vip_purchases(expires_at);

CREATE INDEX idx_daily_tasks_user_id_date ON daily_tasks(user_id, date);
CREATE INDEX idx_daily_tasks_date ON daily_tasks(date);

CREATE INDEX idx_leaderboards_period_category ON leaderboards(period, category);
CREATE INDEX idx_leaderboards_score ON leaderboards(score DESC);
CREATE INDEX idx_leaderboards_user_id ON leaderboards(user_id);

CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_created_at ON analytics(created_at);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leaderboards_updated_at BEFORE UPDATE ON leaderboards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Materialized View for daily statistics
CREATE MATERIALIZED VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_games,
    SUM(CASE WHEN win_amount > 0 THEN 1 ELSE 0 END) as winning_games,
    SUM(bet_amount) as total_wagered,
    COALESCE(SUM(win_amount), 0) as total_winnings,
    COUNT(DISTINCT CASE WHEN tier = 'VIP' THEN user_id END) as vip_users,
    COUNT(DISTINCT CASE WHEN tier = 'Pro' THEN user_id END) as pro_users
FROM games
JOIN users ON games.user_id = users.id
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Refresh the materialized view daily
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW daily_stats;
END;
$$ language 'plpgsql';

-- Sample data for testing
INSERT INTO users (telegram_id, username, first_name, tier, balance) VALUES
(123456789, 'test_user', 'Test User', 'VIP', 10000),
(987654321, 'premium_user', 'Premium User', 'Pro', 5000),
(555555555, 'free_user', 'Free User', 'Free', 100);

-- Create admin user
INSERT INTO users (telegram_id, username, first_name, tier, balance, settings) VALUES
(999999999, 'admin', 'System Admin', 'VIP', 1000000, '{"is_admin": true, "permissions": ["all"]}');

COMMENT ON TABLE users IS 'טבלת משתמשים ראשית';
COMMENT ON TABLE games IS 'טבלת משחקים שהושלמו';
COMMENT ON TABLE transactions IS 'טבלת עסקאות פיננסיות';
COMMENT ON TABLE referrals IS 'טבלת הפניות משתמשים';
COMMENT ON TABLE vip_purchases IS 'טבלת רכישות מנויי VIP';
COMMENT ON TABLE daily_tasks IS 'טבלת משימות יומיות';
COMMENT ON TABLE leaderboards IS 'טבלת לוחות תוצאות';
COMMENT ON TABLE analytics IS 'טבלת נתוני אנליטיקס';
COMMENT ON TABLE notifications IS 'טבלת התראות למשתמשים';
COMMENT ON TABLE audit_logs IS 'יומן פעולות למערכת';

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nifty_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nifty_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO nifty_user;
