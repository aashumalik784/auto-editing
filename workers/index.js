// Cloudflare Worker - Main Entry Point

import { handleAuth } from './src/auth.js';
import { handleQueue } from './src/queue.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    try {
      // Route handling
      if (pathname.startsWith('/auth')) {
        return await handleAuth(request, env);
      }

      if (pathname.startsWith('/queue')) {
        return await handleQueue(request, env);
      }

      // Health check
      if (pathname === '/health') {
        return new Response(JSON.stringify({
          status: 'healthy',
          service: 'auto-editing-worker',
          timestamp: new Date().toISOString()
        }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Default response
      return new Response('Auto-Editing Worker', {
        headers: { 'Content-Type': 'text/plain' }
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal server error',
        message: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
