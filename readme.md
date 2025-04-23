# Raw Socket E-commerce Application

A simple e-commerce application built with raw sockets in Python, allowing communication between server and client machines.

## Overview

This application demonstrates a basic e-commerce system with the following features:

- Product browsing and details viewing
- Shopping cart functionality
- Checkout process
- Order history

The application uses raw TCP sockets for communication between the server and client components.

## Components

### Server (`server.py`)

Handles client connections and processes requests for product information, shopping cart operations, and checkout functionality.

### Client (`client.py`)

Provides a menu-driven interface for users to interact with the e-commerce system. Users can browse products, add items to their cart, and complete purchases.

### Test Client (`test_client.py`)

A utility script that automatically tests all API endpoints to verify server functionality.

## Requirements

- Python 3.6+
- No external dependencies required (uses standard library only)

## Setup and Running

### Server Setup

1. Save the server code to `server.py`
2. Run the server:
   ```
   python3 server.py
   ```
3. The server will display its IP address, which clients need to connect to:
   ```
   E-commerce server started on 0.0.0.0:8888
   Your network IP address: 192.168.x.x
   Clients should connect to: 192.168.x.x:8888
   ```

### Client Setup

1. Save the client code to `client.py`
2. Run the client with the server's IP address:
   ```
   python3 client.py 192.168.x.x
   ```
   (Replace 192.168.x.x with the actual server IP address)

3. Alternatively, edit the `SERVER_HOST` variable in the client code to match your server's IP address

### Quick Testing

To verify the connection and basic functionality:

1. Save the test client code to `test_client.py`
2. Run the test:
   ```
   python3 test_client.py 192.168.x.x
   ```
   (Replace 192.168.x.x with the actual server IP address)

## Client Usage

Once connected, the client presents a menu with the following options:

1. **View products**: Lists all available products with their IDs, names, prices, and stock levels
2. **View product details**: Shows detailed information about a specific product
3. **Add product to cart**: Adds a specified quantity of a product to your shopping cart
4. **View cart**: Displays the current contents of your shopping cart
5. **Checkout**: Processes your order and clears your cart
6. **View orders**: Shows your order history
7. **Test connection**: Verifies connectivity to the server
0. **Exit**: Closes the client application

## Network Configuration

- Both server and client machines must be on the same network
- Default port is 8888 (can be changed in the code if needed)
- If having connection issues, check firewall settings on both machines

## Running Both Components on the Same Machine

You can run both server and client on the same machine:

1. Start the server in one terminal
2. Open another terminal and run the client using either:
   - The displayed IP address from the server
   - `localhost` or `127.0.0.1`

## Troubleshooting

- **Connection refused error**: Ensure the server is running and the correct IP address is being used
- **Firewall issues**: Temporarily disable firewalls to test connectivity
- **Wrong IP address**: Make sure you're using the network IP address displayed by the server
- **Port conflicts**: If port 8888 is in use, modify the port number in both server and client code

## Extending the Application

- Add user authentication
- Implement persistent storage for products and orders
- Add payment processing simulation
- Enhance the product catalog with categories and search functionality
