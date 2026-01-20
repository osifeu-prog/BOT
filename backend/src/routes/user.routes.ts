import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { prisma } from '../db/database';
import { authMiddleware } from '../middleware/auth';
import { z } from 'zod';

const getUserSchema = z.object({
  userId: z.string().transform(val => parseInt(val, 10)),
});

const updateBalanceSchema = z.object({
  amount: z.number().int(),
});

export async function userRoutes(fastify: FastifyInstance) {
  // Get user profile
  fastify.get('/profile', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        
        const user = await prisma.user.findUnique({
          where: { id: userId },
          select: {
            id: true,
            telegramId: true,
            username: true,
            firstName: true,
            lastName: true,
            balanceTokens: true,
            referralCode: true,
            isBanned: true,
            isAdmin: true,
            createdAt: true,
          },
        });
        
        if (!user) {
          return reply.status(404).send({ error: 'User not found' });
        }
        
        return reply.send({ user });
      } catch (error) {
        console.error('Get profile error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
  
  // Get user balance
  fastify.get('/balance', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        
        const user = await prisma.user.findUnique({
          where: { id: userId },
          select: {
            balanceTokens: true,
          },
        });
        
        if (!user) {
          return reply.status(404).send({ error: 'User not found' });
        }
        
        return reply.send({ balance: user.balanceTokens });
      } catch (error) {
        console.error('Get balance error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
  
  // Get user stores
  fastify.get('/stores', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        
        const userStores = await prisma.userStore.findMany({
          where: { userId },
          include: {
            store: true,
          },
          orderBy: { acquiredAt: 'desc' },
        });
        
        return reply.send({ stores: userStores });
      } catch (error) {
        console.error('Get stores error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
  
  // Get game history
  fastify.get('/history', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        const { limit = 20, offset = 0 } = request.query as any;
        
        const history = await prisma.gameHistory.findMany({
          where: { userId },
          orderBy: { createdAt: 'desc' },
          take: parseInt(limit),
          skip: parseInt(offset),
        });
        
        const total = await prisma.gameHistory.count({
          where: { userId },
        });
        
        return reply.send({ history, total });
      } catch (error) {
        console.error('Get history error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
  
  // Get referral stats
  fastify.get('/referrals', {
    preHandler: [authMiddleware],
    handler: async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const userId = (request as any).user?.id;
        
        const user = await prisma.user.findUnique({
          where: { id: userId },
          select: {
            referralCode: true,
          },
        });
        
        if (!user) {
          return reply.status(404).send({ error: 'User not found' });
        }
        
        const referrals = await prisma.user.findMany({
          where: { referredBy: userId },
          select: {
            id: true,
            username: true,
            createdAt: true,
          },
          orderBy: { createdAt: 'desc' },
        });
        
        const referralLink = \`https://t.me/YOUR_BOT_USERNAME?start=\${user.referralCode}\`;
        
        return reply.send({
          referralCode: user.referralCode,
          referralLink,
          totalReferrals: referrals.length,
          referrals,
        });
      } catch (error) {
        console.error('Get referrals error:', error);
        return reply.status(500).send({ error: 'Internal server error' });
      }
    },
  });
}
