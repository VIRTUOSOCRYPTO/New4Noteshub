import { Express } from 'express';
import { createServer, type Server } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import authRoutes from './auth.routes';
import notesRoutes from './notes.routes';
import userRoutes from './user.routes';
import moderationRoutes from './moderation.routes';
import adminRoutes from './admin.routes';
import authRoutesJWT from '../auth-routes';

/**
 * Register all application routes
 */
export async function registerRoutes(app: Express): Promise<Server> {
  // Test Routes for API connectivity troubleshooting
  app.get('/test', (req, res) => {
    res.json({ 
      message: 'CORS is working!',
      timestamp: new Date().toISOString()
    });
  });
  
  // Root path - serve basic info
  app.get('/', (req, res, next) => {
    if (!req.headers.accept || !req.headers.accept.includes('text/html')) {
      return res.json({
        name: 'NotesHub API',
        status: 'running',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development',
        message: 'API server is running. Use /api/health for more detailed status.'
      });
    }
    next();
  });
  
  /**
   * @swagger
   * /api/health:
   *   get:
   *     summary: Health check endpoint
   *     description: Check if the API server is running and responsive
   *     tags: [Health]
   *     security: []
   *     responses:
   *       200:
   *         description: Server is healthy
   *         content:
   *           application/json:
   *             schema:
   *               type: object
   *               properties:
   *                 status:
   *                   type: string
   *                   example: ok
   *                 message:
   *                   type: string
   *                   example: API server is running
   *                 timestamp:
   *                   type: string
   *                   format: date-time
   *                 environment:
   *                   type: string
   *                   example: development
   */
  const healthHandler = (req: any, res: any) => {
    res.json({ 
      status: 'ok', 
      message: 'API server is running',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      host: req.get('host'),
      path: req.path,
      baseUrl: req.baseUrl,
      originalUrl: req.originalUrl,
      headers: req.headers
    });
  };
  
  app.get('/api/health', healthHandler);
  app.get('/health', healthHandler);

  // Register modular routes
  app.use('/api/auth', authRoutes);
  app.use('/api/notes', notesRoutes);
  app.use('/api/user', userRoutes);
  app.use('/api/moderation', moderationRoutes);
  app.use('/api/admin', adminRoutes);
  
  // JWT-based auth routes (additional auth endpoints)
  app.use('/api/auth', authRoutesJWT);

  // Create HTTP server
  const httpServer = createServer(app);
  
  // Create WebSocket server for real-time drawing collaboration
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  
  // Store active drawing connections
  const connections = new Map<string, WebSocket[]>();
  
  wss.on('connection', (ws: WebSocket) => {
    console.log('WebSocket connection established');
    let drawingId: string = "";
    
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        // Handle join drawing room
        if (data.type === 'join' && data.drawingId) {
          drawingId = String(data.drawingId);
          
          if (!connections.has(drawingId)) {
            connections.set(drawingId, []);
          }
          
          const drawingConnections = connections.get(drawingId) || [];
          drawingConnections.push(ws);
          connections.set(drawingId, drawingConnections);
          
          console.log(`Client joined drawing: ${drawingId}, total clients: ${drawingConnections.length}`);
          
          ws.send(JSON.stringify({
            type: 'joined',
            drawingId,
            clients: drawingConnections.length
          }));
        }
        
        // Handle drawing data updates
        if (data.type === 'draw' && drawingId) {
          const drawingConnections = connections.get(drawingId) || [];
          
          drawingConnections.forEach(client => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({
                type: 'draw',
                drawData: data.drawData
              }));
            }
          });
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    });
    
    // Handle disconnection
    ws.on('close', () => {
      console.log('WebSocket connection closed');
      
      if (drawingId) {
        const drawingConnections = connections.get(drawingId) || [];
        const updatedConnections = drawingConnections.filter(client => client !== ws);
        
        if (updatedConnections.length === 0) {
          connections.delete(drawingId);
          console.log(`Drawing room ${drawingId} closed (no clients)`);
        } else {
          connections.set(drawingId, updatedConnections);
          console.log(`Client left drawing ${drawingId}, remaining clients: ${updatedConnections.length}`);
          
          updatedConnections.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({
                type: 'clientLeft',
                clients: updatedConnections.length
              }));
            }
          });
        }
      }
    });
  });
  
  return httpServer;
}
