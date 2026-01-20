import crypto from 'crypto';

export function generateReferralCode(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export function generateToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function validateTelegramId(id: string): boolean {
  return /^\d+$/.test(id) && id.length >= 5;
}

export function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

export function calculatePassiveIncome(stores: any[]): number {
  return stores.reduce((total, userStore) => {
    return total + (userStore.store.passiveIncomePerHour || 0);
  }, 0);
}

export function getRandomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function shuffleArray<T>(array: T[]): T[] {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

export function generateGameId(): string {
  return \`GAME-\${Date.now()}-\${Math.random().toString(36).substr(2, 9)}\`;
}

export function calculateWinChance(baseChance: number, bonusPercent: number): number {
  return Math.min(baseChance + bonusPercent, 95); // Max 95% chance
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}
