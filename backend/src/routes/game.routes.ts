import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { prisma } from '../db/database';
import { authMiddleware } from '../middleware/auth';
import { 
  playRoulette, 
  playDice, 
  playBlackjack, 
  playWheel 
} from '../games';
import { z } from 'zod';

const playGameSchema = z.object({
  gameType: z.enum(['roulette', 'dice', 'blackjack', 'wheel']),
  bet: z.number().int().min(1),
  options: z.record(z.any()).optional(),
});

export async function gameRoutes(fastify: FastifyInstance) {
  // Play game
  fastify.post('/play', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        const { gameType, bet, options } = playGameSchema.parse(request.body);
        
        // Get user with balance check
        const user = await prisma.user.findUnique({
          where: { id: userId },
        });
        
        if (!user) {
          return reply.status(404).send({ error: 'User not found' });
        }
        
        if (user.balanceTokens < bet) {
          return reply.status(400).send({ error: 'Insufficient balance' });
        }
        
        // Deduct bet amount
        await prisma.user.update({
          where: { id: userId },
          data: {
            balanceTokens: {
              decrement: bet,
            },
          },
        });
        
        // Record transaction
        await prisma.transaction.create({
          data: {
            userId,
            type: 'game_bet',
            amount: -bet,
            balanceBefore: user.balanceTokens,
            balanceAfter: user.balanceTokens - bet,
            description: \`\${gameType} bet\`,
            metadata: { gameType, bet, options },
          },
        });
        
        // Play game
        let result;
        const gameParams = { bet, ...options };
        
        switch (gameType) {
          case 'roulette':
            result = await playRoulette(user, gameParams);
            break;
          case 'dice':
            result = await playDice(user, gameParams);
            break;
          case 'blackjack':
            result = await playBlackjack(user, gameParams);
            break;
          case 'wheel':
            result = await playWheel(user, gameParams);
            break;
          default:
            return reply.status(400).send({ error: 'Invalid game type' });
        }
        
        if (!result.success) {
          return reply.status(500).send({ error: result.message });
        }
        
        // Update balance with winnings/losses
        const newBalance = user.balanceTokens - bet + result.amount;
        
        await prisma.user.update({
          where: { id: userId },
          data: {
            balanceTokens: newBalance,
          },
        });
        
        // Record game history
        await prisma.gameHistory.create({
          data: {
            userId,
            gameType,
            betAmount: bet,
            winAmount: result.win ? result.amount : 0,
            result: result.win ? 'win' : 'loss',
            metadata: result.data,
          },
        });
        
        // Record win/loss transaction
        if (result.amount !== 0) {
          await prisma.transaction.create({
            data: {
              userId,
              type: result.win ? 'game_win' : 'game_loss',
              amount: result.amount,
              balanceBefore: user.balanceTokens - bet,
              balanceAfter: newBalance,
              description: \`\${gameType} \${result.win ? 'win' : 'loss'}\`,
              metadata: { gameType, result: result.data },
            },
          });
        }
        
        return reply.send({
          success: true,
          win: result.win,
          amount: result.amount,
          message: result.message,
          data: result.data,
          newBalance,
        });
      } catch (error) {
        console.error('Play game error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
  
  // Get available games
  fastify.get('/available', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const games = [
          {
            id: 'roulette',
            name: 'Roulette',
            description: 'Classic casino roulette wheel',
            minBet: 5,
            maxBet: 1000,
            entryCost: 10,
          },
          {
            id: 'dice',
            name: 'Dice',
            description: 'Roll the dice and win big',
            minBet: 1,
            maxBet: 500,
            entryCost: 5,
          },
          {
            id: 'blackjack',
            name: 'Blackjack',
            description: 'Beat the dealer in this card game',
            minBet: 10,
            maxBet: 2000,
            entryCost: 20,
          },
          {
            id: 'wheel',
            name: 'Wheel of Fortune',
            description: 'Spin the wheel for amazing prizes',
            minBet: 5,
            maxBet: 1000,
            entryCost: 15,
          },
        ];
        
        return reply.send({ games });
      } catch (error) {
        console.error('Get games error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
}
