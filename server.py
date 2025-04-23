import socket
import json
import threading
import uuid
from datetime import datetime

# Sample product database
products = {
    "1": {"id": "1", "name": "Laptop", "price": 999.99, "description": "High-performance laptop with SSD", "stock": 10},
    "2": {"id": "2", "name": "Smartphone", "price": 499.99, "description": "Latest smartphone model", "stock": 15},
    "3": {"id": "3", "name": "Headphones", "price": 89.99, "description": "Noise-cancelling headphones", "stock": 20},
    "4": {"id": "4", "name": "Smartwatch", "price": 199.99, "description": "Fitness tracking smartwatch", "stock": 8},
    "5": {"id": "5", "name": "Tablet", "price": 349.99, "description": "10-inch tablet with retina display", "stock": 12},
}

# Store active shopping carts
carts = {}

# Store completed orders
orders = {}

def handle_client(client_socket, addr):
    """Handle client connection and process requests"""
    print(f"Client connected from {addr[0]}:{addr[1]}")
    try:
        while True:
            # Receive data from client
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break

            print(f"Received from {addr[0]}:{addr[1]}: {data[:100]}...")
            
            # Parse request
            try:
                request = json.loads(data)
                action = request.get('action')
                
                # Process different actions
                if action == 'get_products':
                    response = {'status': 'success', 'products': products}
                
                elif action == 'get_product':
                    product_id = request.get('product_id')
                    if product_id in products:
                        response = {'status': 'success', 'product': products[product_id]}
                    else:
                        response = {'status': 'error', 'message': 'Product not found'}
                
                elif action == 'create_cart':
                    cart_id = str(uuid.uuid4())
                    carts[cart_id] = {'items': {}, 'created_at': datetime.now().isoformat()}
                    response = {'status': 'success', 'cart_id': cart_id}
                
                elif action == 'add_to_cart':
                    cart_id = request.get('cart_id')
                    product_id = request.get('product_id')
                    quantity = request.get('quantity', 1)
                    
                    if cart_id not in carts:
                        response = {'status': 'error', 'message': 'Cart not found'}
                    elif product_id not in products:
                        response = {'status': 'error', 'message': 'Product not found'}
                    elif products[product_id]['stock'] < quantity:
                        response = {'status': 'error', 'message': 'Insufficient stock'}
                    else:
                        # Add or update item in cart
                        cart = carts[cart_id]
                        if product_id in cart['items']:
                            cart['items'][product_id]['quantity'] += quantity
                        else:
                            cart['items'][product_id] = {
                                'product': products[product_id],
                                'quantity': quantity
                            }
                        response = {'status': 'success', 'cart': cart}
                
                elif action == 'get_cart':
                    cart_id = request.get('cart_id')
                    if cart_id in carts:
                        response = {'status': 'success', 'cart': carts[cart_id]}
                    else:
                        response = {'status': 'error', 'message': 'Cart not found'}
                
                elif action == 'checkout':
                    cart_id = request.get('cart_id')
                    if cart_id not in carts:
                        response = {'status': 'error', 'message': 'Cart not found'}
                    else:
                        cart = carts[cart_id]
                        # Calculate total
                        total = sum(item['product']['price'] * item['quantity'] for item in cart['items'].values())
                        
                        # Create order
                        order_id = str(uuid.uuid4())
                        order = {
                            'id': order_id,
                            'cart': cart,
                            'total': total,
                            'status': 'completed',
                            'created_at': datetime.now().isoformat()
                        }
                        orders[order_id] = order
                        
                        # Update stock
                        for product_id, item in cart['items'].items():
                            products[product_id]['stock'] -= item['quantity']
                        
                        # Remove cart
                        del carts[cart_id]
                        
                        response = {'status': 'success', 'order': order}
                
                elif action == 'get_orders':
                    response = {'status': 'success', 'orders': orders}
                
                else:
                    response = {'status': 'error', 'message': 'Invalid action'}
                
            except json.JSONDecodeError:
                response = {'status': 'error', 'message': 'Invalid JSON'}
            except Exception as e:
                response = {'status': 'error', 'message': str(e)}
            
            # Send response back to client
            response_data = json.dumps(response).encode('utf-8')
            client_socket.send(response_data)
            print(f"Sent response to {addr[0]}:{addr[1]}: {len(response_data)} bytes")
    
    except Exception as e:
        print(f"Error handling client {addr[0]}:{addr[1]}: {e}")
    finally:
        client_socket.close()
        print(f"Connection closed with {addr[0]}:{addr[1]}")

def get_ip_address():
    """Get the actual IP address of this machine on the network"""
    try:
        # Create a temporary socket to determine the outgoing IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

def start_server(host='0.0.0.0', port=8888):  # 0.0.0.0 binds to all interfaces
    """Start e-commerce server with raw sockets"""
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        
        # Get the actual network IP
        server_ip = get_ip_address()
        print(f"E-commerce server started on {host}:{port}")
        print(f"Your network IP address: {server_ip}")
        print(f"Clients should connect to: {server_ip}:{port}")
        
        while True:
            # Accept client connection
            client_sock, addr = server_socket.accept()
            
            # Handle client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        print("Server shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()