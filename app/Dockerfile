# Multi-stage build for React Vite SPA targeting ARM64 / multi-platform

# Stage 1: Build static assets
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

# Build production distribution
RUN npm run build


# Stage 2: Nginx runtime
FROM nginx:alpine AS production

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled SPA assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy both environment-specific configs
COPY default.conf.template /etc/nginx/default.conf.template
COPY default.local.conf /etc/nginx/default.local.conf

# Copy runtime configuration selector
COPY docker-entrypoint-custom.sh /docker-entrypoint-custom.sh

RUN chmod +x /docker-entrypoint-custom.sh

EXPOSE 80 443

ENTRYPOINT ["/docker-entrypoint-custom.sh"]