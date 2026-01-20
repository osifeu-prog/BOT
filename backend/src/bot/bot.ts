import { Telegraf, Context } from 'telegraf';
import { prisma } from '../db/database';
import { config } from '../config/config';
import { generateReferralCode } from '../utils/helpers';
import { 
  sendWelcomeMessage,
  sendBalanceMessage,
  sendStoreMenu,
  sendGameMenu,
  sendPaymentMenu,
  sendAdminMenu 
} from './keyboards';
import { 
  playRoulette, 
  playDice, 
  playBlackjack, 
  playWheel 
} from '../games';

interface BotContext extends Context {
  session?: {
    user?: any;
    gameState?: any;
    paymentState?: any;
  };
}

export function initBot(bot: Telegraf) {
  // Initialize session middleware
  bot.use(async (ctx: BotContext, next) => {
    if (!ctx.session) {
      ctx.session = {};
    }
    
    const telegramId = ctx.from?.id;
    if (telegramId) {
      const user = await getUserOrCreate(telegramId, ctx.from);
      ctx.session.user = user;
    }
    
    await next();
  });

  // Start command
  bot.start(async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;

    // Check for referral
    const startPayload = ctx.startPayload;
    if (startPayload) {
      await handleReferral(user.id, startPayload);
    }

    await sendWelcomeMessage(ctx, user);
  });

  // Balance command
  bot.command('balance', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    await sendBalanceMessage(ctx, user);
  });

  // Games command
  bot.command('games', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    await sendGameMenu(ctx, user);
  });

  // Store command
  bot.command('store', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    await sendStoreMenu(ctx, user);
  });

  // Buy command
  bot.command('buy', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    await sendPaymentMenu(ctx, user);
  });

  // Referral command
  bot.command('referral', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    
    const referralLink = \`https://t.me/\${config.botUsername}?start=\${user.referralCode}\`;
    await ctx.replyWithHTML(
      \`🎁 <b>Referral Program</b>\n\n` +
      \`Invite friends and earn <b>\${config.referralReward}</b> tokens for each friend!\n\n` +
      \`Your referral link:\n<code>\${referralLink}</code>\n\n` +
      \`Share this link with your friends!\`
    );
  });

  // Admin command (only for admin users)
  bot.command('admin', async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user || !user.isAdmin) {
      return ctx.reply('⛔ Access denied');
    }
    await sendAdminMenu(ctx, user);
  });

  // Game callbacks
  bot.action(/^game_(.+)$/, async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    
    const gameType = ctx.match[1];
    await handleGameSelection(ctx, user, gameType);
  });

  // Store purchase callbacks
  bot.action(/^store_(\\d+)$/, async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    
    const storeId = parseInt(ctx.match[1]);
    await handleStorePurchase(ctx, user, storeId);
  });

  // Payment callbacks
  bot.action(/^buy_(\\d+)$/, async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user) return;
    
    const packIndex = parseInt(ctx.match[1]);
    await handleTokenPurchase(ctx, user, packIndex);
  });

  // Admin actions
  bot.action(/^admin_(.+)$/, async (ctx: BotContext) => {
    const user = ctx.session?.user;
    if (!user || !user.isAdmin) return;
    
    const action = ctx.match[1];
    await handleAdminAction(ctx, user, action);
  });

  // Error handling
  bot.catch((err: any, ctx: Context) => {
    console.error('Bot error:', err);
    ctx.reply('❌ An error occurred. Please try again later.');
  });
}

async function getUserOrCreate(telegramId: number, telegramUser: any) {
  let user = await prisma.user.findUnique({
    where: { telegramId: BigInt(telegramId) },
  });

  if (!user) {
    const referralCode = generateReferralCode();
    user = await prisma.user.create({
      data: {
        telegramId: BigInt(telegramId),
        username: telegramUser.username,
        firstName: telegramUser.first_name,
        lastName: telegramUser.last_name,
        languageCode: telegramUser.language_code,
        referralCode,
        balanceTokens: 100, // Starting bonus
      },
    });

    // Record starting bonus transaction
    await prisma.transaction.create({
      data: {
        userId: user.id,
        type: 'welcome_bonus',
        amount: 100,
        balanceBefore: 0,
        balanceAfter: 100,
        description: 'Welcome bonus',
      },
    });
  }

  return user;
}

async function handleReferral(userId: number, referralCode: string) {
  try {
    const referrer = await prisma.user.findUnique({
      where: { referralCode },
    });

    if (referrer && referrer.id !== userId) {
      // Update referredBy for new user
      await prisma.user.update({
        where: { id: userId },
        data: { referredBy: referrer.telegramId },
      });

      // Give reward to referrer
      await prisma.$transaction([
        prisma.user.update({
          where: { id: referrer.id },
          data: {
            balanceTokens: {
              increment: config.referralReward,
            },
          },
        }),
        prisma.transaction.create({
          data: {
            userId: referrer.id,
            type: 'referral',
            amount: config.referralReward,
            balanceBefore: referrer.balanceTokens,
            balanceAfter: referrer.balanceTokens + config.referralReward,
            description: 'Referral reward',
            metadata: { referredUserId: userId },
          },
        }),
      ]);
    }
  } catch (error) {
    console.error('Referral handling error:', error);
  }
}

async function handleGameSelection(ctx: BotContext, user: any, gameType: string) {
  // Check if user has enough balance for entry
  const gameConfig = (config as any).games[gameType];
  if (!gameConfig) {
    return ctx.reply('❌ Game not found');
  }

  if (user.balanceTokens < gameConfig.entryCost) {
    return ctx.reply(\`❌ Insufficient balance. Need \${gameConfig.entryCost} tokens to play.\`);
  }

  // Deduct entry cost
  await prisma.user.update({
    where: { id: user.id },
    data: {
      balanceTokens: {
        decrement: gameConfig.entryCost,
      },
    },
  });

  // Play game based on type
  let result;
  switch (gameType) {
    case 'roulette':
      result = await playRoulette(user, { bet: gameConfig.entryCost });
      break;
    case 'dice':
      result = await playDice(user, { bet: gameConfig.entryCost });
      break;
    case 'blackjack':
      result = await playBlackjack(user, { bet: gameConfig.entryCost });
      break;
    case 'wheel':
      result = await playWheel(user, { bet: gameConfig.entryCost });
      break;
    default:
      return ctx.reply('❌ Unknown game type');
  }

  // Update user balance with winnings/losses
  if (result.success) {
    await prisma.user.update({
      where: { id: user.id },
      data: {
        balanceTokens: {
          increment: result.amount,
        },
      },
    });

    // Record game history
    await prisma.gameHistory.create({
      data: {
        userId: user.id,
        gameType,
        betAmount: gameConfig.entryCost,
        winAmount: result.win ? result.amount : 0,
        result: result.win ? 'win' : 'loss',
        metadata: result.data,
      },
    });

    // Send result to user
    const emoji = result.win ? '🎉' : '💸';
    await ctx.replyWithHTML(
      \`\${emoji} <b>Game Result</b>\n\n` +
      \`Game: <b>\${gameType.toUpperCase()}</b>\n` +
      \`Bet: <b>\${gameConfig.entryCost}</b> tokens\n` +
      \`Result: <b>\${result.message}</b>\n` +
      \`\${result.win ? 'Won' : 'Lost'}: <b>\${Math.abs(result.amount)}</b> tokens\n\n` +
      \`New balance: <b>\${user.balanceTokens + result.amount}</b> tokens\`
    );
  } else {
    await ctx.reply(\`❌ Game error: \${result.message}\`);
  }
}

async function handleStorePurchase(ctx: BotContext, user: any, storeId: number) {
  const store = config.stores.find(s => s.id === storeId);
  if (!store) {
    return ctx.reply('❌ Store not found');
  }

  // Check if user already owns this store
  const existingStore = await prisma.userStore.findFirst({
    where: {
      userId: user.id,
      storeId: store.id,
    },
  });

  if (existingStore) {
    return ctx.reply('✅ You already own this store!');
  }

  // Check balance
  if (user.balanceTokens < store.price) {
    return ctx.reply(\`❌ Insufficient balance. Need \${store.price} tokens.\`);
  }

  // Purchase store
  try {
    await prisma.$transaction([
      prisma.user.update({
        where: { id: user.id },
        data: {
          balanceTokens: {
            decrement: store.price,
          },
        },
      }),
      prisma.userStore.create({
        data: {
          userId: user.id,
          storeId: store.id,
        },
      }),
      prisma.transaction.create({
        data: {
          userId: user.id,
          type: 'store_purchase',
          amount: -store.price,
          balanceBefore: user.balanceTokens,
          balanceAfter: user.balanceTokens - store.price,
          description: \`Purchased \${store.name}\`,
          metadata: { storeId: store.id, storeName: store.name },
        },
      }),
    ]);

    await ctx.replyWithHTML(
      \`🏪 <b>Store Purchased!</b>\n\n` +
      \`You have successfully purchased <b>\${store.name}</b>!\n\n` +
      \`Benefits:\n` +
      \`• +\${store.bonusPercent}% win chance bonus\n` +
      \`• +\${store.passiveIncome} tokens/hour passive income\n\n` +
      \`New balance: <b>\${user.balanceTokens - store.price}</b> tokens\`
    );
  } catch (error) {
    console.error('Store purchase error:', error);
    await ctx.reply('❌ Failed to purchase store. Please try again.');
  }
}

async function handleTokenPurchase(ctx: BotContext, user: any, packIndex: number) {
  const packs = config.tokenPacks;
  if (packIndex < 0 || packIndex >= packs.length) {
    return ctx.reply('❌ Invalid pack selection');
  }

  const amount = packs[packIndex];
  await ctx.replyWithHTML(
    \`💰 <b>Token Purchase</b>\n\n` +
    \`Selected pack: <b>\${amount}</b> tokens\n\n` +
    \`Please send <b>\${amount / 100} TON</b> to:\n` +
    \`<code>\${config.tonWallet}</code>\n\n` +
    \`After payment, forward the transaction receipt here.\`
  );

  // Store payment state
  ctx.session!.paymentState = {
    userId: user.id,
    amount,
    currency: 'TON',
    awaitingPayment: true,
  };
}

async function handleAdminAction(ctx: BotContext, user: any, action: string) {
  switch (action) {
    case 'stats':
      await showAdminStats(ctx);
      break;
    case 'users':
      await listUsers(ctx);
      break;
    case 'broadcast':
      await ctx.reply('📢 Broadcast feature coming soon...');
      break;
    case 'config':
      await showConfig(ctx);
      break;
  }
}

async function showAdminStats(ctx: BotContext) {
  const [
    totalUsers,
    activeUsers,
    totalBalance,
    gamesPlayed,
    totalStoresSold,
    revenueToday,
  ] = await Promise.all([
    prisma.user.count(),
    prisma.user.count({ where: { updatedAt: { gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } } }),
    prisma.user.aggregate({ _sum: { balanceTokens: true } }),
    prisma.gameHistory.count(),
    prisma.userStore.count(),
    prisma.transaction.aggregate({
      _sum: { amount: true },
      where: {
        type: 'store_purchase',
        createdAt: { gte: new Date(new Date().setHours(0, 0, 0, 0)) },
      },
    }),
  ]);

  await ctx.replyWithHTML(
    \`📊 <b>Admin Statistics</b>\n\n` +
    \`Total Users: <b>\${totalUsers}</b>\n` +
    \`Active Users (7d): <b>\${activeUsers}</b>\n` +
    \`Total Balance: <b>\${totalBalance._sum.balanceTokens || 0}</b> tokens\n` +
    \`Games Played: <b>\${gamesPlayed}</b>\n` +
    \`Stores Sold: <b>\${totalStoresSold}</b>\n` +
    \`Revenue Today: <b>\${revenueToday._sum.amount || 0}</b> tokens\n`
  );
}

async function listUsers(ctx: BotContext) {
  const users = await prisma.user.findMany({
    take: 10,
    orderBy: { createdAt: 'desc' },
    select: {
      id: true,
      username: true,
      balanceTokens: true,
      isBanned: true,
      createdAt: true,
    },
  });

  let message = '👥 <b>Recent Users</b>\n\n';
  users.forEach(user => {
    const status = user.isBanned ? '🚫' : '✅';
    message += \`\${status} @\${user.username || 'No username'} - \${user.balanceTokens} tokens\n\`;
  });

  await ctx.replyWithHTML(message);
}

async function showConfig(ctx: BotContext) {
  await ctx.replyWithHTML(
    \`⚙️ <b>System Configuration</b>\n\n` +
    \`Referral Reward: <b>\${config.referralReward}</b> tokens\n` +
    \`Win Chance: <b>\${config.winChancePercent}%</b>\n` +
    \`Peek Cost: <b>\${config.peekCost}</b> tokens\n` +
    \`Token Packs: <b>\${config.tokenPacks.join(', ')}</b>\n`
  );
}
