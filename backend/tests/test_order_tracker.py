import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

@pytest.fixture
def sample_order():
    """
    Provides sample order data for reuse across tests.
    """
    return {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001"
    }

@pytest.mark.parametrize("status,expected_status", [
    (None, "pending"),           # Default status
    ("shipped", "shipped"),       # Explicit status
    ("delivered", "delivered"),   # Another explicit status
])
def test_add_order_with_status(order_tracker, mock_storage, sample_order, status, expected_status):
    """Tests adding a new order with default or explicit status."""
    kwargs = {
        "order_id": sample_order["order_id"],
        "item_name": sample_order["item_name"],
        "quantity": sample_order["quantity"],
        "customer_id": sample_order["customer_id"]
    }
    if status:
        kwargs["status"] = status
    
    order_tracker.add_order(**kwargs)
    
    # Verify save_order was called with correct status
    args, call_kwargs = mock_storage.save_order.call_args
    saved_data = args[1]
    assert saved_data["status"] == expected_status

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

@pytest.mark.parametrize("order_id,expected", [
    ("ORD001", {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1}),
    ("NONEXISTENT", None),
])
def test_get_order_by_id(order_tracker, mock_storage, order_id, expected):
    """Tests retrieving orders - both existing and non-existent."""
    mock_storage.get_order.return_value = expected
    
    result = order_tracker.get_order_by_id(order_id)
    
    assert result == expected
    mock_storage.get_order.assert_called_once_with(order_id)

@pytest.mark.parametrize("invalid_id", ["", "   "])
def test_get_order_by_id_invalid_id_raises_error(order_tracker, invalid_id):
    """Tests that getting an order with empty or whitespace ID raises ValueError."""
    with pytest.raises(ValueError, match="Order ID cannot be empty."):
        order_tracker.get_order_by_id(invalid_id)

@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_add_order_invalid_quantity(order_tracker, quantity):
    """Tests that adding an order with invalid quantity raises ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD002", "Item", quantity, "CUST001")

@pytest.mark.parametrize("field,value,error_message", [
    ("order_id", "", "Order ID cannot be empty."),
    ("item_name", "", "Item name cannot be empty."),
    ("customer_id", "", "Customer ID cannot be empty."),
])
def test_add_order_missing_required_fields(order_tracker, field, value, error_message):
    """Tests that adding an order with missing required fields raises ValueError."""
    kwargs = {
        "order_id": "ORD002",
        "item_name": "Item",
        "quantity": 1,
        "customer_id": "CUST001"
    }
    kwargs[field] = value
    
    with pytest.raises(ValueError, match=error_message):
        order_tracker.add_order(**kwargs)

def test_add_order_with_invalid_status(order_tracker):
    """Tests that adding an order with invalid status raises ValueError."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.add_order("ORD002", "Item", 1, "CUST001", status="invalid_status")
