/**
 * Swagger/OpenAPI Documentation Configuration
 * Provides interactive API documentation at /api-docs
 */
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';

const options: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'NotesHub API Documentation',
      version: '1.0.0',
      description: `
        NotesHub API - A platform for students to share and discover study notes.
        
        ## Features
        - User authentication (email/password and Google OAuth)
        - Two-factor authentication (2FA)
        - Note upload, download, and search
        - Bookmarking system
        - Direct messaging between users
        - Drawing/collaboration features
        - Moderation and admin controls
        
        ## Authentication
        Most endpoints require authentication. After logging in, a session cookie
        will be set automatically. Include this cookie in subsequent requests.
        
        ## Rate Limiting
        - API endpoints: 100 requests per 15 minutes
        - Auth endpoints: 10 requests per 15 minutes
      `,
      contact: {
        name: 'NotesHub Support',
        email: 'support@noteshub.example.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:5000',
        description: 'Development server'
      },
      {
        url: 'https://notezhub.onrender.com',
        description: 'Production server'
      }
    ],
    tags: [
      {
        name: 'Authentication',
        description: 'User authentication and account management'
      },
      {
        name: 'Notes',
        description: 'Note upload, search, and management'
      },
      {
        name: 'User',
        description: 'User profile and settings'
      },
      {
        name: 'Bookmarks',
        description: 'Bookmark management'
      },
      {
        name: 'Messages',
        description: 'Direct messaging between users'
      },
      {
        name: 'Moderation',
        description: 'Content moderation endpoints'
      },
      {
        name: 'Admin',
        description: 'Administrative operations'
      },
      {
        name: 'Health',
        description: 'API health and status checks'
      }
    ],
    components: {
      securitySchemes: {
        cookieAuth: {
          type: 'apiKey',
          in: 'cookie',
          name: 'connect.sid',
          description: 'Session cookie set after successful login'
        }
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            id: { type: 'integer', example: 1 },
            usn: { type: 'string', example: '1SI20CS045' },
            email: { type: 'string', format: 'email', example: 'student@college.edu' },
            department: { type: 'string', example: 'CSE' },
            college: { type: 'string', example: 'rvce' },
            year: { type: 'integer', minimum: 1, maximum: 4, example: 1 },
            profilePicture: { type: 'string', nullable: true },
            notifyNewNotes: { type: 'boolean', example: true },
            notifyDownloads: { type: 'boolean', example: false },
            twoFactorEnabled: { type: 'boolean', example: false },
            createdAt: { type: 'string', format: 'date-time' }
          }
        },
        Note: {
          type: 'object',
          properties: {
            id: { type: 'integer', example: 1 },
            userId: { type: 'integer', example: 1 },
            usn: { type: 'string', example: '1SI20CS045' },
            title: { type: 'string', example: 'Data Structures Notes' },
            department: { type: 'string', example: 'CSE' },
            year: { type: 'integer', example: 1 },
            subject: { type: 'string', example: 'Data Structures' },
            filename: { type: 'string', example: 'ds_notes_1234.pdf' },
            originalFilename: { type: 'string', example: 'DS_Notes.pdf' },
            uploadedAt: { type: 'string', format: 'date-time' },
            isFlagged: { type: 'boolean', example: false },
            flagReason: { type: 'string', nullable: true },
            isApproved: { type: 'boolean', example: true }
          }
        },
        Error: {
          type: 'object',
          properties: {
            error: { type: 'string', example: 'Error message' },
            statusCode: { type: 'integer', example: 400 }
          }
        },
        PaginationMeta: {
          type: 'object',
          properties: {
            page: { type: 'integer', example: 1 },
            limit: { type: 'integer', example: 20 },
            total: { type: 'integer', example: 100 },
            totalPages: { type: 'integer', example: 5 },
            hasNext: { type: 'boolean', example: true },
            hasPrev: { type: 'boolean', example: false }
          }
        }
      },
      responses: {
        UnauthorizedError: {
          description: 'Authentication required',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                error: 'Please log in to access this resource',
                statusCode: 401
              }
            }
          }
        },
        ForbiddenError: {
          description: 'Insufficient permissions',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                error: 'You do not have permission to perform this action',
                statusCode: 403
              }
            }
          }
        },
        NotFoundError: {
          description: 'Resource not found',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                error: 'Resource not found',
                statusCode: 404
              }
            }
          }
        },
        ValidationError: {
          description: 'Invalid request data',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                error: 'Validation failed: password must be at least 8 characters',
                statusCode: 400
              }
            }
          }
        }
      }
    },
    security: [
      {
        cookieAuth: []
      }
    ]
  },
  apis: [
    './server/routes/*.ts',
    './server/routes/*.js',
    './server/index.ts'
  ]
};

const swaggerSpec = swaggerJsdoc(options);

/**
 * Setup Swagger documentation endpoint
 */
export function setupSwagger(app: Express): void {
  // Swagger UI endpoint
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'NotesHub API Docs'
  }));

  // Swagger JSON endpoint
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(swaggerSpec);
  });

  console.log('📚 Swagger documentation available at: /api-docs');
}

export default swaggerSpec;
