# CDN Integration Guide for NotesHub

This guide explains how to integrate a CDN (Content Delivery Network) for static assets to improve performance.

## Why Use a CDN?

- **Faster Load Times**: Assets served from edge locations closer to users
- **Reduced Bandwidth**: Less load on your origin server
- **Better Caching**: Automatic caching of static assets
- **DDoS Protection**: Additional security layer
- **Global Reach**: Better performance for international users

## Recommended CDN Providers

### 1. Cloudflare (Recommended - Free Tier Available)

**Pros:**
- Free tier with unlimited bandwidth
- Automatic HTTPS
- DDoS protection
- Easy setup
- Global CDN network

**Setup Steps:**

1. **Sign up for Cloudflare**: https://dash.cloudflare.com/sign-up

2. **Add Your Domain**:
   - Enter your domain name
   - Cloudflare will scan your DNS records

3. **Update Nameservers**:
   - Update your domain's nameservers to Cloudflare's
   - Wait for DNS propagation (can take up to 24 hours)

4. **Configure Caching Rules**:
   ```
   Page Rules:
   - Pattern: yourdomain.com/static/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month
   ```

5. **Enable Auto Minify**:
   - Go to Speed > Optimization
   - Enable Auto Minify for HTML, CSS, JS

6. **Enable Brotli Compression**:
   - Go to Speed > Optimization
   - Enable Brotli

### 2. AWS CloudFront

**Pros:**
- Integrates well with S3
- Pay-as-you-go pricing
- Advanced features

**Setup Steps:**

1. **Create S3 Bucket** for static assets

2. **Create CloudFront Distribution**:
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name your-bucket.s3.amazonaws.com \
     --default-root-object index.html
   ```

3. **Update Frontend URLs**:
   ```javascript
   // frontend/.env.production
   REACT_APP_CDN_URL=https://d1234567890.cloudfront.net
   ```

### 3. Vercel Edge Network

**Pros:**
- Automatic CDN for Vercel deployments
- Zero configuration
- Free for hobby projects

**Setup**: Deploy frontend to Vercel - CDN is automatic!

## Implementation in NotesHub

### 1. Environment Configuration

Add to `/app/frontend/.env.production`:
```bash
# CDN Configuration
REACT_APP_CDN_ENABLED=true
REACT_APP_CDN_URL=https://cdn.yourdomain.com
```

### 2. Frontend Build Configuration

Update `/app/frontend/vite.config.ts`:
```typescript
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    base: env.REACT_APP_CDN_ENABLED === 'true' 
      ? env.REACT_APP_CDN_URL 
      : '/',
    build: {
      rollupOptions: {
        output: {
          // Add hash to filenames for cache busting
          entryFileNames: 'assets/[name].[hash].js',
          chunkFileNames: 'assets/[name].[hash].js',
          assetFileNames: 'assets/[name].[hash].[ext]'
        }
      }
    }
  }
})
```

### 3. Asset Upload Script

Create `/app/scripts/upload_to_cdn.sh`:
```bash
#!/bin/bash

# Build frontend
cd frontend
yarn build

# Upload to S3 (if using AWS)
if [ "$CDN_PROVIDER" = "aws" ]; then
  aws s3 sync dist/ s3://$S3_BUCKET/static/ \
    --cache-control "max-age=31536000" \
    --exclude "*.html"
  
  # Upload HTML with shorter cache
  aws s3 sync dist/ s3://$S3_BUCKET/ \
    --cache-control "max-age=3600" \
    --exclude "*" --include "*.html"
  
  # Invalidate CloudFront cache
  aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_DIST_ID \
    --paths "/*"
fi

echo "✅ Assets uploaded to CDN"
```

### 4. Cache Headers Configuration

Update `/app/backend/server.py` for uploaded files:
```python
from fastapi.responses import FileResponse
from datetime import datetime, timedelta

@app.get("/api/files/{file_path:path}")
async def serve_file(file_path: str):
    file = f"uploads/{file_path}"
    
    if not os.path.exists(file):
        raise HTTPException(status_code=404)
    
    # Set cache headers
    headers = {
        "Cache-Control": "public, max-age=31536000",  # 1 year
        "ETag": generate_etag(file)
    }
    
    return FileResponse(file, headers=headers)
```

## Caching Strategy

### Static Assets (JS, CSS, Images)
```
Cache-Control: public, max-age=31536000, immutable
```
- Cache for 1 year
- Use versioned filenames (e.g., app.v123.js)

### HTML Files
```
Cache-Control: public, max-age=3600, must-revalidate
```
- Cache for 1 hour
- Always revalidate with server

### API Responses
```
Cache-Control: no-cache, no-store, must-revalidate
```
- Never cache dynamic data

### User-Generated Content
```
Cache-Control: public, max-age=86400
```
- Cache for 24 hours
- Can be cached by CDN

## Cache Invalidation

### Cloudflare
```bash
# Purge everything
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'

# Purge specific files
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://yourdomain.com/style.css"]}'
```

### AWS CloudFront
```bash
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

## Testing CDN Integration

### 1. Check Response Headers
```bash
curl -I https://yourdomain.com/static/app.js

# Look for:
# - CF-Cache-Status: HIT (Cloudflare)
# - X-Cache: Hit from cloudfront (AWS)
# - Age: 3600 (cached for 1 hour)
```

### 2. Test From Different Locations
Use https://www.webpagetest.org/
- Test from multiple geographic locations
- Check Time to First Byte (TTFB)
- Verify assets load from CDN

### 3. Monitor Cache Hit Ratio
- Cloudflare: Analytics > Caching
- AWS: CloudWatch > CloudFront metrics
- Target: > 80% cache hit ratio

## Performance Checklist

- [ ] CDN configured and active
- [ ] Appropriate cache headers set
- [ ] Assets versioned for cache busting
- [ ] HTML files have short cache TTL
- [ ] Static assets have long cache TTL
- [ ] Compression enabled (gzip/brotli)
- [ ] Image optimization configured
- [ ] Cache invalidation process documented
- [ ] Monitoring alerts configured

## Troubleshooting

### Assets Not Loading from CDN
1. Check DNS configuration
2. Verify CDN distribution is deployed
3. Check CORS headers
4. Verify asset paths are correct

### Cache Not Working
1. Check Cache-Control headers
2. Verify CDN caching rules
3. Check for Set-Cookie headers (prevents caching)
4. Review query strings (may bypass cache)

### Stale Content
1. Implement cache invalidation
2. Use versioned filenames
3. Reduce cache TTL for frequently changing content

## Cost Estimation

### Cloudflare (Free Tier)
- Cost: $0/month
- Bandwidth: Unlimited
- Requests: Unlimited
- SSL: Included

### AWS CloudFront
- Data Transfer: $0.085/GB (first 10TB)
- Requests: $0.0075 per 10,000 HTTP requests
- Estimated: $10-50/month for small apps

### Vercel
- Free tier: 100GB bandwidth
- Pro: $20/month (1TB bandwidth)

## Next Steps

1. Choose CDN provider (Cloudflare recommended for free tier)
2. Configure DNS and CDN
3. Update build configuration
4. Test thoroughly
5. Monitor performance improvements
6. Set up cache invalidation workflow
