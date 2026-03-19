# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def _validate_order_id(self, order_id):
        if not order_id or not str(order_id).strip():
            raise ValueError("Order ID cannot be empty.")

    def _validate_status(self, status):
        if not status or not str(status).strip():
            raise ValueError("Status cannot be empty.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}.")

    def _normalize_orders(self, orders):
        if orders is None:
            return []
        if isinstance(orders, dict):
            return list(orders.values())
        if isinstance(orders, list):
            return orders.copy()
        raise TypeError("Storage.get_all_orders() must return dict or list")

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        # Validate required fields
        self._validate_order_id(order_id)
        if not item_name or not item_name.strip():
            raise ValueError("Item name cannot be empty.")
        if not customer_id or not customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")

        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        # Validate status
        self._validate_status(status)
        
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
        self._validate_order_id(order_id)
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        self._validate_order_id(order_id)
        self._validate_status(new_status)

        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        updated_order = order.copy() if isinstance(order, dict) else dict(order)
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)
        return updated_order

    def list_all_orders(self):
        orders = self.storage.get_all_orders()
        return self._normalize_orders(orders)

    def list_orders_by_status(self, status: str):
        if not status or not str(status).strip():
            raise ValueError("Status cannot be empty.")

        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")

        orders = self.list_all_orders()
        return [order for order in orders if order.get("status") == status]
