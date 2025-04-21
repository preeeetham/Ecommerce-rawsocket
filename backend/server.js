const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const cors = require("cors");
require("dotenv").config(); // This loads environment variables from the .env file

const app = express();
const server = http.createServer(app);

// Allow requests from ecom.com (or any domain defined in your .env file)
app.use(cors({
  origin: process.env.FRONTEND_URI, // Your e-commerce website domain
}));

const wss = new WebSocket.Server({ server });

// Track global user count and users viewing specific items
let clientCount = 0;
const productViews = {}; // Object to keep track of users viewing each product

wss.on("connection", (ws) => {
  clientCount++;
  broadcastUserCount();

  // When a new client sends a message (either to change item or chat)
  ws.on("message", (data) => {
    try {
      const message = JSON.parse(data);

      // Handling the user viewing a particular product
      if (message.type === "viewProduct") {
        const { productId } = message;
        if (productId) {
          // Track which product the user is viewing
          if (!productViews[productId]) {
            productViews[productId] = new Set();
          }
          productViews[productId].add(ws);
          broadcastProductViewCount(productId); // Broadcast updated view count for the product
        }
      }

      // Handling chat messages
      if (message.type === "chat") {
        const { productId, username, text } = message;
        if (productId && productViews[productId]) {
          // Send chat message to all users viewing the same product
          broadcastChat(productId, {
            username: username || "Anonymous", // Default username
            text,
            time: new Date().toLocaleTimeString(),
          });
        }
      }
    } catch (error) {
      console.error("Failed to parse incoming message", error);
    }
  });

  // When a user disconnects
  ws.on("close", () => {
    clientCount--;
    broadcastUserCount();

    // Remove the user from all product views
    for (const productId in productViews) {
      productViews[productId].delete(ws);
      broadcastProductViewCount(productId); // Broadcast updated view count for the product
    }
  });
});

// Broadcast user count to all connected clients
function broadcastUserCount() {
  const message = JSON.stringify({ type: "userCount", count: clientCount });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// Broadcast the number of users viewing a particular product
function broadcastProductViewCount(productId) {
  const viewersCount = productViews[productId]?.size || 0;
  const message = JSON.stringify({ type: "productViewCount", productId, viewersCount });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// Broadcast a chat message to all users viewing the same product
function broadcastChat(productId, chatMessage) {
  const message = JSON.stringify({
    type: "chat",
    productId,
    ...chatMessage,
  });

  // Send the message to users viewing the same product
  productViews[productId]?.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

const PORT = 3001;
server.listen(PORT, () => {
  console.log(`✅ WebSocket server running on http://localhost:${PORT}`);
});
