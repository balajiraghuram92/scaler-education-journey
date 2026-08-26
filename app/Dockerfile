# Multi-stage build for React Vite SPA targeting ARM64 / multi-platform

# Stage 1: Build static assets
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder

WORKDIR /app

# The API base URL is non-secret and may be set for a separately hosted API.
# Authentication is injected by the same-origin Nginx proxy at runtime.
ARG VITE_API_BASE_URL=""

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
