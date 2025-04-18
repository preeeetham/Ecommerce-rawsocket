// server.js
const express = require("express");
const http = require("http");
const WebSocket = require("ws");

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let clientCount = 0;

wss.on("connection", (ws) => {
  clientCount++;
  broadcastClientCount();

  ws.on("close", () => {
    clientCount--;
    broadcastClientCount();
  });
});

function broadcastClientCount() {
  const message = JSON.stringify({ type: "userCount", count: clientCount });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
      console.log(`Sent message to client: ${message}`);
    }
  });
}

const PORT = 3001;
server.listen(PORT, () => {
  console.log(`WebSocket server running on http://localhost:${PORT}`);
});


//asdfaksdlfkad