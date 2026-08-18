# Multi-stage build for React Vite SPA targeting ARM64 / multi-platform

# Stage 1: Build static assets
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./

# Install dependencies cleanly
RUN npm ci

# Copy application source
COPY . .

# Accept build arguments from GitHub Actions / Docker CLI
ARG VITE_API_KEY
ENV VITE_API_KEY=$VITE_API_KEY

# Build production distribution with baked environment variables
RUN npm run build

# Stage 2: Production Nginx runtime (runs as native ARM64 on EC2)
FROM nginx:alpine AS production

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled SPA assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA fallback and API reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
