#this is where tickets will be initialized and stored

from db_config import execute_query

def get_routes():
    """Get all ticket routes from the database."""
    query = """
        SELECT ticket_id, event, tier, price, availability, created_at 
        FROM tickets 
        ORDER BY CAST(SUBSTRING(ticket_id, 5) AS UNSIGNED), event, tier
    """
    return execute_query(query, fetch=True)

def get_ticket(ticket_id):
    """Get a specific ticket by ID."""
    query = """
        SELECT ticket_id, event, tier, price, availability, created_at 
        FROM tickets 
        WHERE ticket_id = %s
    """
    result = execute_query(query, (ticket_id,), fetch=True)
    return result[0] if result else None

def add_route(ticket_data):
    """Add a new ticket route to the database."""
    query = """
        INSERT INTO tickets (ticket_id, event, tier, price, availability, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """
    params = (
        ticket_data['ticket_id'],
        ticket_data['event'],
        ticket_data['tier'],
        ticket_data['price'],
        ticket_data['availability']
    )
    execute_query(query, params)

def remove_route(ticket_index):
    """Remove a ticket route from the database."""
    # First get the ticket_id for the given index
    routes = get_routes()
    if 0 <= ticket_index < len(routes):
        ticket_id = routes[ticket_index]['ticket_id']
        query = "DELETE FROM tickets WHERE ticket_id = %s"
        execute_query(query, (ticket_id,))

def update_route(ticket_index, ticket_data):
    """Update an existing ticket route in the database."""
    query = """
        UPDATE tickets 
        SET event = %s, tier = %s, price = %s, availability = %s
        WHERE ticket_id = %s
    """
    params = (
        ticket_data['event'],
        ticket_data['tier'],
        ticket_data['price'],
        ticket_data['availability'],
        ticket_data['ticket_id']
    )
    execute_query(query, params)

def update_ticket_availability(ticket_index, ticket_data):
    """Update only the availability of a ticket."""
    query = """
        UPDATE tickets 
        SET availability = %s
        WHERE ticket_id = %s
    """
    params = (
        ticket_data['availability'],
        ticket_data['ticket_id']
    )
    execute_query(query, params)

def get_next_ticket_id():
    """Get the next available ticket ID in EVT-XXX format."""
    query = """
        SELECT ticket_id 
        FROM tickets 
        WHERE ticket_id LIKE 'EVT-%' 
        ORDER BY CAST(SUBSTRING(ticket_id, 5) AS UNSIGNED) DESC 
        LIMIT 1
    """
    result = execute_query(query, fetch=True)
    
    if result and result[0]['ticket_id']:
        # Extract the number part and increment
        last_num = int(result[0]['ticket_id'].split('-')[1])
        next_num = last_num + 1
    else:
        # If no existing tickets, start with 1
        next_num = 1
    
    # Format as EVT-XXX with leading zeros
    return f"EVT-{str(next_num).zfill(3)}"