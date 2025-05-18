#this is where tickets will be initialized and stored

routes_data = [
    {"ticket_id": "EVT-001", "event": "Coldplay", "tier": "Standard Seating", "price": 2500, "availability": 120},
    {"ticket_id": "EVT-002", "event": "Coldplay", "tier": "Silver Seating", "price": 4000, "availability": 80},
    {"ticket_id": "EVT-003", "event": "Coldplay", "tier": "Gold Seating", "price": 7000, "availability": 30},
    {"ticket_id": "EVT-004", "event": "Rex Orange County", "tier": "Standard Seating", "price": 1800, "availability": 100},
    {"ticket_id": "EVT-005", "event": "Rex Orange County", "tier": "Silver Seating", "price": 3200, "availability": 60},
    {"ticket_id": "EVT-006", "event": "Rex Orange County", "tier": "Gold Seating", "price": 6000, "availability": 20},
    {"ticket_id": "EVT-007", "event": "Apo Hiking Society", "tier": "Standard Seating", "price": 1500, "availability": 150},
    {"ticket_id": "EVT-008", "event": "Apo Hiking Society", "tier": "Silver Seating", "price": 2500, "availability": 90},
    {"ticket_id": "EVT-009", "event": "Apo Hiking Society", "tier": "Gold Seating", "price": 4000, "availability": 25},
    {"ticket_id": "EVT-010", "event": "Queen", "tier": "Standard Seating", "price": 3000, "availability": 110},
    {"ticket_id": "EVT-011", "event": "Queen", "tier": "Silver Seating", "price": 5000, "availability": 70},
    {"ticket_id": "EVT-012", "event": "Queen", "tier": "Gold Seating", "price": 9000, "availability": 15},
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
        return "EVT-001"
    last_id = sorted(routes_data, key=lambda x: x["ticket_id"]) [-1]["ticket_id"]
    num = int(last_id.split('-')[1]) + 1
    return f"EVT-{num:03d}"

