# Multi-stage build for React Vite SPA targeting ARM64 / multi-platform

# Stage 1: Build static assets (runs on host build platform for max speed)
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder

WORKDIR /app

# Build arguments from CI/CD secrets for Vite static asset compilation
ARG VITE_API_KEY
ARG VITE_API_BASE_URL=""

ENV VITE_API_KEY=$VITE_API_KEY
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy dependency manifests
COPY package*.json ./

# Install dependencies cleanly
RUN npm ci

# Copy application source
COPY . .

# Build production distribution to /app/dist
RUN npm run build

# Stage 2: Production Nginx runtime (native ARM64 on EC2)
FROM nginx:alpine AS production

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled SPA assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA fallback and API reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
