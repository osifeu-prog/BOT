import { config } from '../config/config';

interface GameParams {
  bet: number;
  section?: number;
}

export async function playWheel(user: any, params: GameParams) {
  try {
    const { bet } = params;
    
    // Calculate win chance with store bonuses
    const userStores = await prisma.userStore.findMany({
      where: { userId: user.id },
      include: { store: true },
    });
    
    const bonusPercent = userStores.reduce(
      (sum, us) => sum + us.store.bonusWinPercent,
      0
    );
    
    const winChance = config.winChancePercent + bonusPercent;
    
    // Wheel of fortune with 12 sections
    const sections = 12;
    const winningSection = Math.floor(Math.random() * sections) + 1;
    
    // Determine multiplier based on section (some sections have higher payouts)
    const multipliers = [1, 2, 3, 5, 10, 2, 3, 5, 2, 3, 1, 20];
    const multiplier = multipliers[winningSection - 1];
    
    // Win based on chance
    const win = Math.random() * 100 < winChance;
    
    if (win) {
      const winnings = bet * multiplier;
      return {
        success: true,
        win: true,
        amount: winnings,
        message: `Wheel landed on section ${winningSection} (${multiplier}x)! You won ${winnings} tokens!`,
        data: { winningSection, multiplier, winChance },
      };
    } else {
      return {
        success: true,
        win: false,
        amount: -bet,
        message: `Wheel landed on section ${winningSection}. You lost.`,
        data: { winningSection, multiplier, winChance },
      };
    }
  } catch (error) {
    console.error('Wheel game error:', error);
    return {
      success: false,
      win: false,
      amount: 0,
      message: 'An error occurred while playing wheel of fortune.',
    };
  }
}
