import socket
import json
import sys
import time

# Server details - CHANGE THIS to the IP address of the server machine
SERVER_HOST = '172.16.0.2'  # Change to server's actual IP address when running on different machines
SERVER_PORT = 8888

class EcommerceClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.cart_id = None
        self.socket = None
    
    def connect(self):
        """Connect to the server"""
        # Create socket and connect
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            print("Disconnected from server")
    
    def send_request(self, request):
        """Send a request to the server and get the response"""
        if not self.socket:
            print("Not connected to server")
            return None
        
        try:
            # Send request
            request_data = json.dumps(request).encode('utf-8')
            self.socket.send(request_data)
            print(f"Sent request: {request['action']}")
            
            # Get response
            response_data = self.socket.recv(8192).decode('utf-8')
            print(f"Received response ({len(response_data)} bytes)")
            return json.loads(response_data)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None
    
    def get_products(self):
        """Get all products"""
        return self.send_request({'action': 'get_products'})
    
    def get_product(self, product_id):
        """Get details of a specific product"""
        return self.send_request({'action': 'get_product', 'product_id': product_id})
    
    def create_cart(self):
        """Create a new shopping cart"""
        response = self.send_request({'action': 'create_cart'})
        if response and response.get('status') == 'success':
            self.cart_id = response.get('cart_id')
            print(f"Created cart with ID: {self.cart_id}")
        return response
    
    def add_to_cart(self, product_id, quantity=1):
        """Add a product to the cart"""
        if not self.cart_id:
            print("No active cart. Creating one...")
            self.create_cart()
        
        return self.send_request({
            'action': 'add_to_cart',
            'cart_id': self.cart_id,
            'product_id': product_id,
            'quantity': quantity
        })
    
    def get_cart(self):
        """Get current cart contents"""
        if not self.cart_id:
            print("No active cart.")
            return None
        
        return self.send_request({
            'action': 'get_cart',
            'cart_id': self.cart_id
        })
    
    def checkout(self):
        """Checkout and create an order"""
        if not self.cart_id:
            print("No active cart to checkout.")
            return None
        
        response = self.send_request({
            'action': 'checkout',
            'cart_id': self.cart_id
        })
        
        if response and response.get('status') == 'success':
            self.cart_id = None  # Reset cart after checkout
            print("Checkout successful!")
        
        return response
    
    def get_orders(self):
        """Get all orders"""
        return self.send_request({'action': 'get_orders'})

def display_menu():
    print("\n===== E-commerce Client Menu =====")
    print("1. View products")
    print("2. View product details")
    print("3. Add product to cart")
    print("4. View cart")
    print("5. Checkout")
    print("6. View orders")
    print("7. Test connection")
    print("0. Exit")
    return input("Select an option: ")

def display_products(products):
    print("\n===== Products =====")
    print(f"{'ID':<5} {'Name':<20} {'Price':<10} {'Stock':<5}")
    print("-" * 45)
    for product_id, product in products.items():
        print(f"{product_id:<5} {product['name']:<20} ${product['price']:<9.2f} {product['stock']:<5}")

def display_cart(cart):
    if not cart or not cart.get('items'):
        print("\nYour cart is empty.")
        return
    
    print("\n===== Your Cart =====")
    print(f"{'Product':<20} {'Price':<10} {'Qty':<5} {'Total':<10}")
    print("-" * 50)
    
    total = 0
    for item_id, item in cart['items'].items():
        product = item['product']
        item_total = product['price'] * item['quantity']
        total += item_total
        print(f"{product['name']:<20} ${product['price']:<9.2f} {item['quantity']:<5} ${item_total:<9.2f}")
    
    print("-" * 50)
    print(f"{'Total:':<36} ${total:<9.2f}")

def test_connection(client):
    """Test the connection by getting products"""
    print("Testing connection to server...")
    start_time = time.time()
    response = client.get_products()
    end_time = time.time()
    
    if response and response.get('status') == 'success':
        print(f"Connection successful! Response time: {(end_time - start_time)*1000:.2f}ms")
        print(f"Retrieved {len(response.get('products', {}))} products")
        return True
    else:
        print("Connection test failed!")
        return False

def main():
    # Get server address from command line if provided
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    else:
        server_host = SERVER_HOST
    
    client = EcommerceClient(host=server_host)
    
    # Connect to server
    if not client.connect():
        print("Exiting due to connection failure.")
        return
    
    try:
        while True:
            choice = display_menu()
            
            if choice == '1':  # View products
                response = client.get_products()
                if response and response.get('status') == 'success':
                    display_products(response.get('products', {}))
                else:
                    print("Failed to retrieve products.")
            
            elif choice == '2':  # View product details
                product_id = input("Enter product ID: ")
                response = client.get_product(product_id)
                if response and response.get('status') == 'success':
                    product = response.get('product')
                    print(f"\nProduct Details for {product['name']}")
                    print(f"ID: {product['id']}")
                    print(f"Price: ${product['price']:.2f}")
                    print(f"Description: {product['description']}")
                    print(f"Stock: {product['stock']}")
                else:
                    print("Failed to retrieve product details.")
            
            elif choice == '3':  # Add product to cart
                product_id = input("Enter product ID: ")
                try:
                    quantity = int(input("Enter quantity: "))
                    if quantity <= 0:
                        print("Quantity must be positive.")
                        continue
                except ValueError:
                    print("Invalid quantity.")
                    continue
                
                response = client.add_to_cart(product_id, quantity)
                if response and response.get('status') == 'success':
                    print(f"Added {quantity} x product {product_id} to cart.")
                else:
                    print(f"Failed to add to cart: {response.get('message', 'Unknown error')}")
            
            elif choice == '4':  # View cart
                response = client.get_cart()
                if response and response.get('status') == 'success':
                    display_cart(response.get('cart'))
                else:
                    print("Failed to retrieve cart.")
            
            elif choice == '5':  # Checkout
                response = client.get_cart()
                if response and response.get('status') == 'success':
                    cart = response.get('cart')
                    if not cart or not cart.get('items'):
                        print("Your cart is empty. Nothing to checkout.")
                        continue
                    
                    display_cart(cart)
                    confirm = input("\nConfirm checkout (y/n): ").lower()
                    if confirm == 'y':
                        checkout_response = client.checkout()
                        if checkout_response and checkout_response.get('status') == 'success':
                            order = checkout_response.get('order')
                            print(f"\nOrder #{order['id']} confirmed!")
                            print(f"Total: ${order['total']:.2f}")
                            print("Thank you for your purchase!")
                        else:
                            print(f"Checkout failed: {checkout_response.get('message', 'Unknown error')}")
                else:
                    print("Failed to retrieve cart.")
            
            elif choice == '6':  # View orders
                response = client.get_orders()
                if response and response.get('status') == 'success':
                    orders = response.get('orders', {})
                    if not orders:
                        print("No orders found.")
                    else:
                        print("\n===== Your Orders =====")
                        for order_id, order in orders.items():
                            print(f"Order #{order_id}")
                            print(f"Date: {order['created_at']}")
                            print(f"Total: ${order['total']:.2f}")
                            print(f"Status: {order['status']}")
                            print("-" * 30)
                else:
                    print("Failed to retrieve orders.")
            
            elif choice == '7':  # Test connection
                test_connection(client)
            
            elif choice == '0':  # Exit
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()