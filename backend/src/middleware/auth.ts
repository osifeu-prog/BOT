import { FastifyRequest, FastifyReply } from 'fastify';
import jwt from 'jsonwebtoken';
import { prisma } from '../db/database';
import { config } from '../config/config';

export interface AuthPayload {
  userId: number;
  telegramId: bigint;
  isAdmin: boolean;
}

export async function authMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const token = extractToken(request);
    if (!token) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const payload = verifyToken(token) as AuthPayload;
    if (!payload) {
      return reply.status(401).send({ error: 'Invalid token' });
    }

    // Check if user exists and is not banned
    const user = await prisma.user.findUnique({
      where: { id: payload.userId },
      select: { id: true, isBanned: true, isAdmin: true },
    });

    if (!user || user.isBanned) {
      return reply.status(401).send({ error: 'User not found or banned' });
    }

    // Attach user to request
    (request as any).user = {
      id: user.id,
      telegramId: payload.telegramId,
      isAdmin: user.isAdmin,
    };
  } catch (error) {
    console.error('Auth middleware error:', error);
    return reply.status(401).send({ error: 'Authentication failed' });
  }
}

export function generateToken(payload: AuthPayload): string {
  return jwt.sign(payload, config.adminPassword, {
    expiresIn: '7d',
  });
}

function extractToken(request: FastifyRequest): string | null {
  const authHeader = request.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return null;
  }
  return authHeader.substring(7);
}

function verifyToken(token: string): AuthPayload | null {
  try {
    return jwt.verify(token, config.adminPassword) as AuthPayload;
  } catch {
    return null;
  }
}
