import { prisma } from '../db/database';
import { config } from '../config/config';
import { calculateWinChance } from '../utils/helpers';
import type { GameResult } from '../types';

interface RouletteParams {
  bet: number;
  number?: number;
  color?: 'red' | 'black' | 'green';
}

export async function playRoulette(user: any, params: RouletteParams): Promise<GameResult> {
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
    
    // European roulette: 37 numbers (0-36)
    const winningNumber = Math.floor(Math.random() * 37);
    const isRed = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(winningNumber);
    const isBlack = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35].includes(winningNumber);
    const isGreen = winningNumber === 0;
    
    // Determine win based on chance
    const win = Math.random() * 100 < winChance;
    
    if (win) {
      // Different payouts based on bet type
      let multiplier = 2; // Default for color bet
      if (params.number !== undefined) {
        multiplier = 36; // Straight up bet
      } else if (params.color === 'green') {
        multiplier = 36; // Green pays 36:1
      }
      
      const winnings = bet * multiplier;
      
      return {
        success: true,
        win: true,
        amount: winnings,
        message: \`Roulette: Number \${winningNumber} (\${isGreen ? 'Green' : isRed ? 'Red' : 'Black'})! You won \${winnings} tokens!\`,
        data: { 
          winningNumber, 
          color: isGreen ? 'green' : isRed ? 'red' : 'black',
          multiplier,
          winChance 
        },
      };
    } else {
      return {
        success: true,
        win: false,
        amount: -bet,
        message: \`Roulette: Number \${winningNumber} (\${isGreen ? 'Green' : isRed ? 'Red' : 'Black'}). You lost.\`,
        data: { 
          winningNumber, 
          color: isGreen ? 'green' : isRed ? 'red' : 'black',
          winChance 
        },
      };
    }
  } catch (error) {
    console.error('Roulette game error:', error);
    return {
      success: false,
      win: false,
      amount: 0,
      message: 'An error occurred while playing roulette.',
    };
  }
}
