# MakeAMix - Docker Deployment for CapRover

This guide will help you deploy your Flask application to CapRover using Docker.

## Files Created for Deployment

1. **Dockerfile** - Multi-stage Docker build configuration
2. **requirements.txt** - Python dependencies
3. **captain-definition** - CapRover deployment configuration
4. **.dockerignore** - Files to exclude from Docker build

## Prerequisites

- CapRover instance running and accessible
- CapRover CLI installed locally (optional)

## Environment Variables

Configure these environment variables in CapRover for your app:

### Required
- `SECRET_KEY`: A strong secret key for Flask sessions (generate a random 32+ character string)
- `DATABASE_URL`: Database connection string (PostgreSQL recommended for production)

### Optional
- `FLASK_ENV`: Set to `production` (default in Dockerfile)

### Example Environment Variables
```
SECRET_KEY=your-super-secret-key-here-should-be-very-long-and-random
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

## Deployment Options

### Option 1: Using CapRover Web Interface

1. **Create a new app** in CapRover dashboard
2. **Upload your code** as a tar.gz file:
   ```bash
   tar --exclude-from=.dockerignore -czf makeamix.tar.gz .
   ```
3. **Upload the tar.gz** file in the deployment section
4. **Configure environment variables** in the app settings
5. **Enable HTTPS** (recommended)

### Option 2: Using Git Integration

1. **Push your code** to a Git repository (GitHub, GitLab, etc.)
2. **Create a new app** in CapRover
3. **Connect the Git repository** in the deployment section
4. **Configure environment variables**
5. **Set up automatic deployments** (optional)

### Option 3: Using CapRover CLI

1. **Install CapRover CLI**:
   ```bash
   npm install -g caprover
   ```

2. **Login to your CapRover**:
   ```bash
   caprover login
   ```

3. **Deploy the app**:
   ```bash
   caprover deploy
   ```

## Database Setup

### Using PostgreSQL (Recommended)

1. **Create a PostgreSQL app** in CapRover or use an external database
2. **Set the DATABASE_URL** environment variable:
   ```
   DATABASE_URL=postgresql://username:password@srv-captain--postgres:5432/makeamix
   ```

### Using SQLite (Development only)

If you don't set DATABASE_URL, the app will use SQLite. Note that SQLite files won't persist between container restarts in CapRover unless you set up persistent volumes.

## File Uploads

The app handles file uploads for songs and mix covers. Files are stored in `/app/src/static/uploads/` inside the container. For production, consider:

1. **Using persistent volumes** in CapRover for file storage
2. **Using cloud storage** (AWS S3, Google Cloud Storage, etc.)
3. **Configuring a CDN** for better performance

## Health Check

The Dockerfile includes a health check that pings the root endpoint. CapRover will use this to ensure your app is running properly.

## Performance Considerations

- The app runs with **4 Gunicorn workers** by default
- **120-second timeout** for requests (good for file uploads)
- Consider increasing resources if you expect high traffic
- Monitor memory usage, especially with file uploads

## Troubleshooting

### Common Issues

1. **App won't start**: Check environment variables and logs
2. **Database connection errors**: Verify DATABASE_URL format
3. **File upload issues**: Check container storage and permissions
4. **Memory issues**: Increase app memory allocation in CapRover

### Viewing Logs

In CapRover dashboard:
1. Go to your app
2. Click on "App Logs" tab
3. Monitor startup and runtime logs

### Testing Locally

Build and test the Docker image locally:

```bash
# Build the image
docker build -t makeamix .

# Run locally
docker run -p 3000:3000 \
  -e SECRET_KEY=test-secret-key \
  -e DATABASE_URL=sqlite:///app.db \
  makeamix
```

## Security Notes

- Never commit your SECRET_KEY to version control
- Use strong, unique passwords for database connections
- Enable HTTPS in CapRover for production
- Regularly update dependencies for security patches

## Scaling

For high-traffic scenarios:
- Increase Gunicorn workers in Dockerfile
- Use multiple app instances in CapRover
- Set up load balancing
- Consider using Redis for session storage
- Implement caching strategies