import Fastify from 'fastify';
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';
import rateLimit from '@fastify/rate-limit';
import { Telegraf } from 'telegraf';
import { fastifyTelegraf } from 'fastify-telegraf';
import { config } from './config/config';
import { initBot } from './bot/bot';
import { userRoutes } from './routes/user.routes';
import { gameRoutes } from './routes/game.routes';
import { storeRoutes } from './routes/store.routes';
import { paymentRoutes } from './routes/payment.routes';
import { adminRoutes } from './routes/admin.routes';
import { initRedis } from './db/redis';
import { initDatabase } from './db/database';
import { errorHandler } from './middleware/errorHandler';
import { authMiddleware } from './middleware/auth';

async function buildServer() {
  const fastify = Fastify({
    logger: config.debugMode
      ? { level: 'info', transport: { target: 'pino-pretty' } }
      : false,
  });

  // Initialize database and cache
  await initDatabase();
  await initRedis();

  // Register security plugins
  await fastify.register(helmet);
  await fastify.register(cors, {
    origin: config.corsOrigins,
    credentials: true,
  });
  await fastify.register(rateLimit, {
    max: 100,
    timeWindow: '1 minute',
  });

  // Setup Telegraf bot
  const bot = new Telegraf(config.telegramToken);
  initBot(bot);

  // Register bot with webhook support
  await fastify.register(fastifyTelegraf, {
    bot,
    path: '/webhook',
  });

  // Register custom error handler
  fastify.setErrorHandler(errorHandler);

  // Register routes
  fastify.register(userRoutes, { prefix: '/api/users' });
  fastify.register(gameRoutes, { prefix: '/api/games' });
  fastify.register(storeRoutes, { prefix: '/api/stores' });
  fastify.register(paymentRoutes, { prefix: '/api/payments' });
  fastify.register(adminRoutes, { prefix: '/api/admin' });

  // Health check endpoint
  fastify.get('/health', async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });

  return fastify;
}

async function startServer() {
  try {
    const server = await buildServer();
    const address = await server.listen({
      port: config.port,
      host: config.host,
    });
    console.log(`🚀 Server listening at ${address}`);
    
    // Setup webhook in production
    if (config.isProduction && config.webhookUrl) {
      const bot = server.bot;
      await bot.telegram.setWebhook(`${config.webhookUrl}/webhook`);
      console.log(`✅ Webhook set to: ${config.webhookUrl}/webhook`);
    }
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

startServer();
