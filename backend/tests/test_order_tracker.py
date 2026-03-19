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

@pytest.fixture
def sample_orders():
    """Provides bulk orders that can be reused across list-related tests."""
    return {
        "ORD1": {"order_id": "ORD1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "ORD2": {"order_id": "ORD2", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"},
        "ORD3": {"order_id": "ORD3", "item_name": "C", "quantity": 1, "customer_id": "C3", "status": "pending"},
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


def test_update_order_status_success(order_tracker, mock_storage):
    """Tests update_order_status updates status when order exists and new status is valid."""
    existing_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }
    mock_storage.get_order.return_value = existing_order

    updated = order_tracker.update_order_status("ORD001", "shipped")

    assert updated["status"] == "shipped"
    assert existing_order["status"] == "pending"  # no in-place mutation
    assert updated is not existing_order

    mock_storage.get_order.assert_called_once_with("ORD001")
    mock_storage.save_order.assert_called_once_with("ORD001", updated)


def test_update_order_status_invalid_status_fails_fast_no_storage_read(order_tracker, mock_storage):
    """Tests invalid status raises before calling storage.get_order."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.update_order_status("ORD001", "not-a-status")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_nonexistent_order_raises(order_tracker, mock_storage):
    """Tests updating status for non-existent order raises ValueError."""
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="does not exist"):
        order_tracker.update_order_status("ORD_DOES_NOT_EXIST", "shipped")


def test_update_order_status_empty_order_id_raises(order_tracker):
    """Tests empty order_id raises ValueError."""
    with pytest.raises(ValueError, match="Order ID cannot be empty"):
        order_tracker.update_order_status("", "shipped")


def test_list_all_orders_empty_storage(order_tracker):
    """Tests that list_all_orders returns empty list when no orders present."""
    assert order_tracker.list_all_orders() == []


def test_list_all_orders_multiple_orders(order_tracker, mock_storage, sample_orders):
    """Tests list_all_orders returns all orders independent of order ordering."""
    mock_storage.get_all_orders.return_value = sample_orders

    results = order_tracker.list_all_orders()

    assert {order["order_id"] for order in results} == {"ORD1", "ORD2", "ORD3"}


@pytest.mark.parametrize("status,expected_ids", [
    ("pending", {"ORD1", "ORD3"}),
    ("shipped", {"ORD2"}),
    ("cancelled", set()),
])
def test_list_orders_by_status(order_tracker, mock_storage, sample_orders, status, expected_ids):
    """Tests list_orders_by_status for matching and non-matching results."""
    mock_storage.get_all_orders.return_value = sample_orders

    results = order_tracker.list_orders_by_status(status)

    assert {order["order_id"] for order in results} == expected_ids


def test_list_orders_by_status_empty_storage(order_tracker):
    """Tests list_orders_by_status returns only matching status orders."""
    orders_dict = {
        "ORD1": {"order_id": "ORD1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "ORD2": {"order_id": "ORD2", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"},
        "ORD3": {"order_id": "ORD3", "item_name": "C", "quantity": 1, "customer_id": "C3", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders_dict

    results = order_tracker.list_orders_by_status("pending")

    assert len(results) == 2
    assert all(order["status"] == "pending" for order in results)


def test_list_orders_by_status_none_match(order_tracker, mock_storage):
    """Tests list_orders_by_status returns empty list when no orders match."""
    orders_dict = {
        "ORD1": {"order_id": "ORD1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "processing"},
        "ORD2": {"order_id": "ORD2", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "cancelled"},
    }
    mock_storage.get_all_orders.return_value = orders_dict

    results = order_tracker.list_orders_by_status("shipped")

    assert results == []


def test_list_orders_by_status_empty_storage(order_tracker):
    """Tests list_orders_by_status returns empty list when storage has no orders."""
    assert order_tracker.list_orders_by_status("pending") == []


def test_list_orders_by_status_invalid_status_raises(order_tracker):
    """Tests list_orders_by_status raises for empty/invalid status."""
    with pytest.raises(ValueError, match="Status cannot be empty"):
        order_tracker.list_orders_by_status("")

    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.list_orders_by_status("invalid")


def test_valid_statuses_constant():
    """Ensures the status set is defined and immutable in a single place."""
    from ..order_tracker import OrderTracker

    assert set(OrderTracker.VALID_STATUSES) == {"pending", "processing", "shipped", "delivered", "cancelled"}

