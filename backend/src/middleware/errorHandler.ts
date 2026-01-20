import { FastifyError, FastifyRequest, FastifyReply } from 'fastify';
import { ZodError } from 'zod';
import { config } from '../config/config';

export function errorHandler(
  error: FastifyError,
  request: FastifyRequest,
  reply: FastifyReply
) {
  // Log error in development
  if (config.debugMode) {
    console.error('Error:', {
      message: error.message,
      stack: error.stack,
      url: request.url,
      method: request.method,
      body: request.body,
    });
  }

  // Handle Zod validation errors
  if (error instanceof ZodError) {
    return reply.status(400).send({
      error: 'Validation error',
      details: error.errors.map(e => ({
        path: e.path.join('.'),
        message: e.message,
      })),
    });
  }

  // Handle specific error codes
  if (error.statusCode) {
    return reply.status(error.statusCode).send({
      error: error.message,
    });
  }

  // Handle database errors
  if ((error as any).code?.startsWith('P')) {
    return reply.status(400).send({
      error: 'Database error occurred',
    });
  }

  // Default error
  return reply.status(500).send({
    error: config.isProduction ? 'Internal server error' : error.message,
  });
}
