import { Context } from 'telegraf';
import { InlineKeyboardButton } from 'telegraf/typings/core/types/typegram';
import { prisma } from '../db/database';
import { config } from '../config/config';

interface BotContext extends Context {
  session?: any;
}

export async function sendWelcomeMessage(ctx: BotContext, user: any) {
  const keyboard = [
    [
      { text: '🎮 Play Games', callback_data: 'games' },
      { text: '🏪 Store', callback_data: 'store' },
    ],
    [
      { text: '💰 Balance', callback_data: 'balance' },
      { text: '💳 Buy Tokens', callback_data: 'buy' },
    ],
    [
      { text: '🎁 Referral', callback_data: 'referral' },
    ],
  ];

  if (user.isAdmin) {
    keyboard.push([{ text: '⚙️ Admin Panel', callback_data: 'admin' }]);
  }

  await ctx.replyWithHTML(
    \`🎰 <b>Welcome to Casino Bot, \${user.firstName || 'Player'}!</b>\n\n` +
    \`Your balance: <b>\${user.balanceTokens}</b> tokens\n` +
    \`Referral code: <code>\${user.referralCode}</code>\n\n` +
    \`Choose an option below:\`,
    {
      reply_markup: {
        inline_keyboard: keyboard,
      },
    }
  );
}

export async function sendBalanceMessage(ctx: BotContext, user: any) {
  // Calculate passive income from stores
  const userStores = await prisma.userStore.findMany({
    where: { userId: user.id },
    include: { store: true },
  });

  const totalPassiveIncome = userStores.reduce(
    (sum, us) => sum + us.store.passiveIncomePerHour,
    0
  );

  const totalBonusPercent = userStores.reduce(
    (sum, us) => sum + us.store.bonusWinPercent,
    0
  );

  await ctx.replyWithHTML(
    \`💰 <b>Your Balance</b>\n\n` +
    \`Tokens: <b>\${user.balanceTokens}</b>\n` +
    \`Stores owned: <b>\${userStores.length}</b>\n` +
    \`Passive income: <b>\${totalPassiveIncome}</b> tokens/hour\n` +
    \`Win bonus: <b>+\${totalBonusPercent}%</b>\n` +
    \`Total win chance: <b>\${config.winChancePercent + totalBonusPercent}%</b>\`
  );
}

export async function sendGameMenu(ctx: BotContext, user: any) {
  const keyboard = [
    [
      { text: '🎡 Roulette', callback_data: 'game_roulette' },
      { text: '🎲 Dice', callback_data: 'game_dice' },
    ],
    [
      { text: '🃏 Blackjack', callback_data: 'game_blackjack' },
      { text: '🎡 Wheel of Fortune', callback_data: 'game_wheel' },
    ],
    [
      { text: '🔙 Back', callback_data: 'back_to_main' },
    ],
  ];

  await ctx.replyWithHTML(
    \`🎮 <b>Choose a Game</b>\n\n` +
    \`Current balance: <b>\${user.balanceTokens}</b> tokens\n\n` +
    \`Available games:\`,
    {
      reply_markup: {
        inline_keyboard: keyboard,
      },
    }
  );
}

export async function sendStoreMenu(ctx: BotContext, user: any) {
  const userStores = await prisma.userStore.findMany({
    where: { userId: user.id },
    include: { store: true },
  });

  const ownedStoreIds = userStores.map(us => us.storeId);

  const keyboard = config.stores.map(store => {
    const owned = ownedStoreIds.includes(store.id);
    return [{
      text: \`\${owned ? '✅ ' : ''}\${store.name} - \${store.price} tokens\`,
      callback_data: \`store_\${store.id}\`,
    }];
  });

  keyboard.push([{ text: '🔙 Back', callback_data: 'back_to_main' }]);

  let message = \`🏪 <b>Available Stores</b>\n\n` +
    \`Balance: <b>\${user.balanceTokens}</b> tokens\n\n` +
    \`Stores provide:\n` +
    \`• Increased win chance\n` +
    \`• Passive token income\n\n` +
    \`Select a store to purchase:\`;

  await ctx.replyWithHTML(message, {
    reply_markup: {
      inline_keyboard: keyboard,
    },
  });
}

export async function sendPaymentMenu(ctx: BotContext, user: any) {
  const keyboard = config.tokenPacks.map((amount, index) => {
    return [{
      text: \`\${amount} tokens - \${amount / 100} TON\`,
      callback_data: \`buy_\${index}\`,
    }];
  });

  keyboard.push([{ text: '🔙 Back', callback_data: 'back_to_main' }]);

  await ctx.replyWithHTML(
    \`💳 <b>Buy Tokens</b>\n\n` +
    \`Current balance: <b>\${user.balanceTokens}</b> tokens\n\n` +
    \`Select a token pack:\`,
    {
      reply_markup: {
        inline_keyboard: keyboard,
      },
    }
  );
}

export async function sendAdminMenu(ctx: BotContext, user: any) {
  const keyboard = [
    [
      { text: '📊 Statistics', callback_data: 'admin_stats' },
      { text: '👥 Users', callback_data: 'admin_users' },
    ],
    [
      { text: '📢 Broadcast', callback_data: 'admin_broadcast' },
      { text: '⚙️ Configuration', callback_data: 'admin_config' },
    ],
    [
      { text: '🔙 Back', callback_data: 'back_to_main' },
    ],
  ];

  await ctx.replyWithHTML(
    \`⚙️ <b>Admin Panel</b>\n\n` +
    \`Welcome, Admin!\n` +
    \`Select an option below:\`,
    {
      reply_markup: {
        inline_keyboard: keyboard,
      },
    }
  );
}
