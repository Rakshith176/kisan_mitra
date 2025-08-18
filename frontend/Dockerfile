# Multi-stage Dockerfile for Flutter Frontend
# Stage 1: Build Flutter Web App
FROM node:18 as flutter-builder

# Install Flutter dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:$PATH"
RUN flutter doctor --android-licenses || true
RUN flutter config --enable-web

# Create non-root user for Flutter
RUN useradd --create-home --shell /bin/bash flutter
RUN chown -R flutter:flutter /flutter

# Set working directory for Flutter
WORKDIR /app

# Copy Flutter project files as root first
COPY . .

# Clean up any existing .dart_tool directory and change ownership
RUN rm -rf .dart_tool && chown -R flutter:flutter /app

# Switch to non-root user
USER flutter

# Install Flutter dependencies and build web app
RUN flutter pub get
RUN flutter build web --release

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Install curl for health check
RUN apk add --no-cache curl

# Copy built Flutter web app
COPY --from=flutter-builder /app/build/web /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
