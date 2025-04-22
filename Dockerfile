# Use the official Node.js image
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Expose port (for socket server)
EXPOSE 9090

# Start the app
CMD ["npx", "ts-node", "src/server.ts"]
