from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    id: str
    items: list[str]
    total: float
    customer_email: str

@dataclass
class ValidatedOrder:
    order: Order
    validated_at: datetime

@dataclass
class ChargedOrder:
    order: ValidatedOrder
    charge_id: str

@dataclass
class Receipt:
    order_id: str
    charge_id: str
    total: float
    items: list[str]

def validate_order(order: Order) -> ValidatedOrder:
    return ValidatedOrder(order=order, validated_at=datetime.now())

def charge_payment(validated: ValidatedOrder) -> ChargedOrder:
    return ChargedOrder(order=validated, charge_id="ch_123")

def generate_receipt(charged: ChargedOrder) -> Receipt:
    return Receipt(
        order_id=charged.order.order.id,
        charge_id=charged.charge_id,
        total=charged.order.order.total,
        items=charged.order.order.items,
    )
