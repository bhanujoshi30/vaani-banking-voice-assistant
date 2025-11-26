# --- STAGE 1: Build the static files ---
# Use a Node base image for building the app
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Expose build-time arg to set the API base URL for Vite
# Defaults to the public API host so production builds call the correct backend.
ARG VITE_API_BASE_URL=https://api.sunnationalbank.online
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Run your Vite build script (Vite will pick up VITE_API_BASE_URL from env)
RUN npm run build

# --- STAGE 2: Serve the static files with a minimal runtime ---
# Use a smaller base image for the final runtime
FROM node:20-alpine

# Install the 'serve' utility globally (used to serve static files)
RUN npm install -g serve

# Copy the built files from the builder stage
# Default Vite output directory is 'dist'
COPY --from=builder /app/dist /app/dist

# Tell Dokku to run the serve command on its assigned port ($PORT is set to 5000 by Dokku)
# CMD is required when using a Dockerfile for Dokku deployment
CMD ["serve", "-s", "/app/dist", "-l", "5000"]