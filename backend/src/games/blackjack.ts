import { config } from '../config/config';

interface GameParams {
  bet: number;
}

export async function playBlackjack(user: any, params: GameParams) {
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
    
    // Simple blackjack logic
    const playerCards = [
      Math.min(10, Math.floor(Math.random() * 13) + 1),
      Math.min(10, Math.floor(Math.random() * 13) + 1),
    ];
    const dealerCards = [
      Math.min(10, Math.floor(Math.random() * 13) + 1),
      Math.min(10, Math.floor(Math.random() * 13) + 1),
    ];
    
    const playerTotal = playerCards.reduce((a, b) => a + b, 0);
    const dealerTotal = dealerCards.reduce((a, b) => a + b, 0);
    
    // Determine winner
    let win = false;
    if (playerTotal > 21) {
      win = false; // Player bust
    } else if (dealerTotal > 21) {
      win = true; // Dealer bust
    } else if (playerTotal > dealerTotal) {
      win = true; // Player has higher total
    } else if (playerTotal === dealerTotal) {
      // Push - return bet
      return {
        success: true,
        win: false,
        amount: 0,
        message: `Blackjack: Player ${playerTotal} vs Dealer ${dealerTotal}. Push!`,
        data: { playerCards, dealerCards, playerTotal, dealerTotal, winChance },
      };
    }
    
    // Adjust win chance
    if (!win && Math.random() * 100 < winChance) {
      win = true; // Bonus win
    }
    
    if (win) {
      // Win 2x the bet for blackjack
      const winnings = playerTotal === 21 ? bet * 2.5 : bet * 2;
      return {
        success: true,
        win: true,
        amount: winnings,
        message: `Blackjack: Player ${playerTotal} vs Dealer ${dealerTotal}. You won ${winnings} tokens!`,
        data: { playerCards, dealerCards, playerTotal, dealerTotal, winChance },
      };
    } else {
      return {
        success: true,
        win: false,
        amount: -bet,
        message: `Blackjack: Player ${playerTotal} vs Dealer ${dealerTotal}. You lost.`,
        data: { playerCards, dealerCards, playerTotal, dealerTotal, winChance },
      };
    }
  } catch (error) {
    console.error('Blackjack game error:', error);
    return {
      success: false,
      win: false,
      amount: 0,
      message: 'An error occurred while playing blackjack.',
    };
  }
}
