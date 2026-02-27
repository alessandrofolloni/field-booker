FROM node:20-alpine

WORKDIR /app

# Copy package and install dependencies
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose Vite's default dev port
EXPOSE 5173

# Start Vite dev server that listens on 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
