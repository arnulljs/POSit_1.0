#this is where tickets will be initialized and stored

routes_data = [
    {"ticket_id": "TK-001", "from": "Manila", "to": "Cebu", "class": "Economy", "price": 3500, "availability": 5},
    {"ticket_id": "TK-002", "from": "Manila", "to": "Cebu", "class": "Business", "price": 5800, "availability": 32},
    {"ticket_id": "TK-003", "from": "Cebu", "to": "Davao", "class": "Economy", "price": 2900, "availability": 58},
    {"ticket_id": "TK-004", "from": "Manila", "to": "Davao", "class": "Economy", "price": 4200, "availability": 23},
    {"ticket_id": "TK-005", "from": "Davao", "to": "Manila", "class": "Business", "price": 6500, "availability": 15},
]

def get_routes():
    return routes_data

def add_route(route):
    routes_data.append(route)

def remove_route(index):
    if 0 <= index < len(routes_data):
        routes_data.pop(index)

def update_route(index, new_data):
    if 0 <= index < len(routes_data):
        routes_data[index].update(new_data)

def get_next_ticket_id():
    if not routes_data:
        return "TK-001"
    last_id = sorted(routes_data, key=lambda x: x["ticket_id"]) [-1]["ticket_id"]
    num = int(last_id.split('-')[1]) + 1
    return f"TK-{num:03d}"

