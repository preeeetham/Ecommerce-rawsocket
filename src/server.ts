import net from "net";

interface Request {
  route: string;
  method: string;
  body?: any;
  user?: { email: string; role: string };
}

const PORT = 9090;
const clients: net.Socket[] = [];
const users: any[] = [];
const chatHistory: any[] = [];
const products = [{ id: 1, name: "Laptop", price: 1000 }];
let connectionCount = 0;

function send(socket: net.Socket, data: any) {
  socket.write(JSON.stringify(data) + "\n");
}

const server = net.createServer((socket) => {
  clients.push(socket);
  connectionCount++;

  socket.on("data", (data) => {
    let message = data.toString().trim();
    try {
      const req: Request = JSON.parse(message);
      handleRequest(socket, req);
    } catch (err) {
      send(socket, { status: 400, error: "Invalid JSON" });
    }
  });

  socket.on("close", () => {
    const index = clients.indexOf(socket);
    if (index !== -1) clients.splice(index, 1);
    connectionCount--;
  });

  socket.on("error", () => {});
});

function handleRequest(socket: net.Socket, req: Request) {
  const { route, method, body, user } = req;

  if (route === "/api/register" && method === "POST") {
    if (users.find((u) => u.email === body.email)) {
      return send(socket, { status: 400, data: { error: "User exists" } });
    }
    const role = body.email === "admin@example.com" ? "admin" : "user";
    users.push({ email: body.email, password: body.password, role });
    return send(socket, { status: 200, data: { message: "User registered" } });
  }

  if (route === "/api/login" && method === "POST") {
    const u = users.find(
      (u) => u.email === body.email && u.password === body.password
    );
    if (!u) {
      return send(socket, { status: 401, data: { error: "Invalid credentials" } });
    }
    return send(socket, { status: 200, data: { message: `${u.role} logged in`, role: u.role } });
  }

  if (route === "/api/products" && method === "GET") {
    return send(socket, { status: 200, data: { products } });
  }

  if (route === "/api/products" && method === "POST") {
    if (!user || user.role !== "admin") {
      return send(socket, { status: 403, data: { error: "Unauthorized" } });
    }
    products.push(body);
    return send(socket, { status: 200, data: { message: "Product added" } });
  }

  if (route === "/api/chat" && method === "POST") {
    if (!user) {
      return send(socket, { status: 403, data: { error: "Unauthorized" } });
    }
    const chatMsg = {
      user: user.email,
      message: user.role === "admin" ? `🔔 ADMIN: ${body.message}` : body.message,
    };
    chatHistory.push(chatMsg);
    clients.forEach((c) => send(c, { status: 200, data: { chat: chatMsg } }));
    return;
  }

  if (route === "/api/connections" && method === "GET") {
    return send(socket, { status: 200, data: { connections: connectionCount } });
  }

  return send(socket, { status: 404, data: { error: "Not Found" } });
}

server.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
