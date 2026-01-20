import { prisma } from '../db/database';
import { config } from '../config/config';
import { calculateWinChance } from '../utils/helpers';
import type { GameResult } from '../types';

interface DiceParams {
  bet: number;
  guess?: number; // Guess the total (2-12)
}

export async function playDice(user: any, params: DiceParams): Promise<GameResult> {
  try {
    const { bet } = params;
    
    // Get user's stores for bonus calculation
    const userStores = await prisma.userStore.findMany({
      where: { userId: user.id },
      include: { store: true },
    });
    
    const totalBonusPercent = userStores.reduce(
      (sum, us) => sum + us.store.bonusWinPercent,
      0
    );
    
    const winChance = calculateWinChance(config.winChancePercent, totalBonusPercent);
    
    // Roll two dice
    const dice1 = Math.floor(Math.random() * 6) + 1;
    const dice2 = Math.floor(Math.random() * 6) + 1;
    const total = dice1 + dice2;
    
    // Check if user guessed correctly
    const guessedCorrectly = params.guess !== undefined && params.guess === total;
    
    // Win if guessed correctly OR based on chance
    const win = guessedCorrectly || Math.random() * 100 < winChance;
    
    if (win) {
      let multiplier = 1.5;
      let message = \`Dice: \${dice1} + \${dice2} = \${total}\`;
      
      if (guessedCorrectly) {
        multiplier = 6; // 6:1 for guessing exact number
        message += \` (Guessed correctly!)\`;
      } else {
        message += \` (Lucky win!)\`;
      }
      
      const winnings = Math.floor(bet * multiplier);
      
      return {
        success: true,
        win: true,
        amount: winnings,
        message: \`\${message}. You won \${winnings} tokens!\`,
        data: { dice1, dice2, total, guessedCorrectly, multiplier, winChance },
      };
    } else {
      return {
        success: true,
        win: false,
        amount: -bet,
        message: \`Dice: \${dice1} + \${dice2} = \${total}. You lost.\`,
        data: { dice1, dice2, total, winChance },
      };
    }
  } catch (error) {
    console.error('Dice game error:', error);
    return {
      success: false,
      win: false,
      amount: 0,
      message: 'An error occurred while playing dice.',
    };
  }
}
