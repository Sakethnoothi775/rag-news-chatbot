# 🛠️ Railway Deployment Troubleshooting

## ❌ Common Build Errors & Solutions

### Error: `npm run build` failed (exit code 249)

**Cause**: React build process failing, usually due to:
- Missing dependencies
- SCSS compilation issues
- TypeScript errors
- Memory issues

**Solutions**:

#### 1. Fix Dockerfile (Already Applied)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
```

#### 2. Check for SCSS Issues
If SCSS compilation fails, temporarily convert to CSS:
```bash
# In client directory
find src -name "*.scss" -exec mv {} {}.backup \;
# Then rename .scss.backup back to .scss after fixing
```

#### 3. Increase Build Memory
Add to Railway environment variables:
```
NODE_OPTIONS=--max-old-space-size=4096
```

#### 4. Check TypeScript Errors
```bash
cd client
npm run build
# Fix any TypeScript errors shown
```

### Error: Service won't start

**Solutions**:
1. Check environment variables are set
2. Verify port configurations
3. Check service dependencies

### Error: Frontend can't connect to backend

**Solutions**:
1. Set correct `REACT_APP_API_URL`
2. Check CORS settings
3. Verify gateway service is running

## 🔧 Railway-Specific Fixes

### 1. Use Railway's Build Cache
Railway automatically caches `node_modules`, but you can force clean:
```bash
# In Railway dashboard, add environment variable:
RAILWAY_CLEAR_CACHE=true
```

### 2. Check Build Logs
1. Go to Railway dashboard
2. Click on your service
3. View "Logs" tab
4. Look for specific error messages

### 3. Manual Build Test
Test locally first:
```bash
cd client
npm install
npm run build
# If this fails, fix errors before deploying
```

## 🚀 Alternative Deployment Methods

### Option 1: Separate Services
Deploy each service separately on Railway:
1. Backend service
2. Frontend service  
3. Gateway service
4. Database services

### Option 2: Static Frontend
Build frontend locally and serve as static files:
```bash
cd client
npm run build
# Upload build/ folder to Railway
```

### Option 3: Use Railway's React Template
1. Create new Railway project
2. Select "React" template
3. Copy your source code
4. Deploy

## 📊 Debugging Steps

### 1. Check Service Health
```bash
# In Railway dashboard
- Backend: https://your-backend.railway.app/health
- Frontend: https://your-frontend.railway.app
- Gateway: https://your-gateway.railway.app
```

### 2. View Detailed Logs
```bash
# Railway CLI
railway logs --service frontend
railway logs --service backend
```

### 3. Test Locally
```bash
# Test the exact same build process
docker build -t test-frontend ./client
docker run -p 3000:3000 test-frontend
```

## 🔄 Quick Fixes

### If Build Still Fails:

1. **Simplify the build**:
   - Remove SCSS temporarily
   - Remove TypeScript temporarily
   - Use basic CSS

2. **Use Railway's auto-detection**:
   - Remove custom Dockerfile
   - Let Railway detect React automatically
   - Add build command: `npm run build`

3. **Deploy backend only**:
   - Deploy just the Python backend
   - Use a simple HTML frontend
   - Add React later

## 📞 Getting Help

1. **Railway Support**: https://railway.app/discord
2. **Check Logs**: Always check Railway logs first
3. **Test Locally**: Reproduce the error locally
4. **GitHub Issues**: Create issue with full error logs

## ✅ Success Checklist

- [ ] All services show "Healthy" status
- [ ] Frontend loads without errors
- [ ] Backend API responds to requests
- [ ] News ingestion works
- [ ] Chat functionality works
- [ ] No console errors in browser

## 🎯 Next Steps

Once deployed successfully:
1. Test all functionality
2. Set up custom domain
3. Configure monitoring
4. Set up auto-deployment
5. Share your app URL!

Remember: Railway is very reliable, but React builds can be tricky. The key is to test locally first! 🚀
