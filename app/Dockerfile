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

# CRITICAL: Restrict envsubst to DOMAIN_NAME so Nginx internal vars ($host, $uri, etc.) are not erased
ENV NGINX_ENVSUBST_FILTER=DOMAIN_NAME

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled SPA assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy template to Nginx templates directory for automatic substitution on container startup
COPY default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]