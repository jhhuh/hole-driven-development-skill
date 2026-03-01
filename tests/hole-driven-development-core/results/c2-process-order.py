from c2_helpers import Order, Receipt, validate_order, charge_payment, generate_receipt

def process_order(order: Order) -> Receipt:
    validated = validate_order(order)
    charged = charge_payment(validated)
    return generate_receipt(charged)
