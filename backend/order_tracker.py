# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        # Validate required fields
        if not order_id or not order_id.strip():
            raise ValueError("Order ID cannot be empty.")
        if not item_name or not item_name.strip():
            raise ValueError("Item name cannot be empty.")
        if not customer_id or not customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")
        
        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        
        # Validate status
        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")
        
        # Check if order already exists
        existing_order = self.storage.get_order(order_id)
        if existing_order:
            raise ValueError(f"Order with ID '{order_id}' already exists.")
        
        # Create and save the new order
        order_data = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order_data)
        return order_data

    def get_order_by_id(self, order_id: str):
        if not order_id or order_id.strip() == "":
            raise ValueError("Order ID cannot be empty.")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        pass

    def list_all_orders(self):
        pass

    def list_orders_by_status(self, status: str):
        pass
