import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  // Telegram
  TELEGRAM_TOKEN: z.string().min(1, 'Telegram token is required'),
  BOT_USERNAME: z.string().min(1, 'Bot username is required'),
  WEBHOOK_URL: z.string().url().optional(),
  
  // Admin
  ADMIN_ID: z.string().transform(val => parseInt(val, 10)),
  ADMIN_USERNAME: z.string().min(1),
  ADMIN_PASSWORD: z.string().min(8),
  
  // Database
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  
  // Payments
  CRYPTO_PAY_TOKEN: z.string().optional(),
  TON_WALLET: z.string().optional(),
  
  // Economy
  TOKEN_PACKS: z.string().transform(val => JSON.parse(val) as number[]),
  REFERRAL_REWARD: z.string().transform(val => parseInt(val, 10)),
  WIN_CHANCE_PERCENT: z.string().transform(val => parseInt(val, 10)),
  PEEK_COST: z.string().transform(val => parseInt(val, 10)),
  
  // Misc
  DEBUG_MODE: z.string().transform(val => val === 'true'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().transform(val => parseInt(val, 10)).default('3001'),
  HOST: z.string().default('0.0.0.0'),
});

const env = envSchema.parse(process.env);

export const config = {
  // Telegram
  telegramToken: env.TELEGRAM_TOKEN,
  botUsername: env.BOT_USERNAME,
  webhookUrl: env.WEBHOOK_URL,
  
  // Admin
  adminId: env.ADMIN_ID,
  adminUsername: env.ADMIN_USERNAME,
  adminPassword: env.ADMIN_PASSWORD,
  
  // Server
  port: env.PORT,
  host: env.HOST,
  isProduction: env.NODE_ENV === 'production',
  debugMode: env.DEBUG_MODE,
  
  // Database
  databaseUrl: env.DATABASE_URL,
  redisUrl: env.REDIS_URL,
  
  // Payments
  cryptoPayToken: env.CRYPTO_PAY_TOKEN,
  tonWallet: env.TON_WALLET,
  
  // Economy
  tokenPacks: env.TOKEN_PACKS,
  referralReward: env.REFERRAL_REWARD,
  winChancePercent: env.WIN_CHANCE_PERCENT,
  peekCost: env.PEEK_COST,
  
  // CORS
  corsOrigins: env.NODE_ENV === 'production' 
    ? ['https://your-domain.com'] 
    : ['http://localhost:3000', 'http://localhost:3001'],
  
  // Game configurations
  games: {
    roulette: {
      entryCost: 10,
      minBet: 5,
      maxBet: 1000,
    },
    dice: {
      entryCost: 5,
      minBet: 1,
      maxBet: 500,
    },
    blackjack: {
      entryCost: 20,
      minBet: 10,
      maxBet: 2000,
    },
    wheel: {
      entryCost: 15,
      minBet: 5,
      maxBet: 1000,
    },
  },
  
  // Store configurations
  stores: [
    {
      id: 1,
      name: 'Basic Shop',
      price: 100,
      bonusPercent: 5,
      passiveIncome: 1,
    },
    {
      id: 2,
      name: 'Premium Shop',
      price: 500,
      bonusPercent: 15,
      passiveIncome: 5,
    },
    {
      id: 3,
      name: 'VIP Casino',
      price: 2000,
      bonusPercent: 30,
      passiveIncome: 20,
    },
  ],
} as const;

export type Config = typeof config;
