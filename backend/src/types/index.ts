export interface User {
  id: number;
  telegramId: bigint;
  username?: string;
  firstName?: string;
  lastName?: string;
  balanceTokens: number;
  referralCode: string;
  referredBy?: number;
  isBanned: boolean;
  isAdmin: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Store {
  id: number;
  name: string;
  description: string;
  priceTokens: number;
  level: number;
  bonusWinPercent: number;
  passiveIncomePerHour: number;
  isActive: boolean;
  createdAt: Date;
}

export interface UserStore {
  id: number;
  userId: number;
  storeId: number;
  acquiredAt: Date;
  store: Store;
}

export interface GameResult {
  success: boolean;
  win: boolean;
  amount: number;
  message: string;
  data?: Record<string, any>;
}

export interface PaymentRequest {
  userId: number;
  amountTokens: number;
  currency: string;
  paymentMethod: string;
}

export interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalBalance: number;
  gamesPlayed: number;
  totalStoresSold: number;
  revenueToday: number;
}

export interface TelegramUser {
  id: number;
  is_bot?: boolean;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}
