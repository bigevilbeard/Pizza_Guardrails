import json
import random
import string

def generate_random_customer_id():
    return f"C{random.randint(100, 999)}"

def generate_random_name():
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name):
    username = name.lower().replace(" ", ".")
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "example.com", "pizza.com"]
    return f"{username}{random.randint(1, 999)}@{random.choice(domains)}"

def generate_random_phone():
    return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_random_feedback():
    feedback_templates = [
        "Too salty for my taste",
        "Delicious pizza!",
        "Could use more toppings",
        "Crust was perfect",
        "Arrived cold",
        "Best pizza in town",
        "Spicy but good",
        "Needs more cheese",
        "Great flavor combination",
        "Disappointed with the quality"
    ]
    return random.choice(feedback_templates)

def generate_random_pizza_type():
    pizza_types = ["Supreme", "Margherita", "Pepperoni", "Vegetarian", "Hawaiian", 
                   "Meat Lover's", "BBQ Chicken", "Four Cheese", "Mushroom", "Veggie Deluxe"]
    return random.choice(pizza_types)

def generate_random_rating():
    return round(random.uniform(1.0, 5.0), 1)

def generate_claude_batch_entries(num_entries):
    entries = []
    for i in range(1, num_entries + 1):
        name = generate_random_name()
        customer_id = generate_random_customer_id()
        feedback_type = generate_random_feedback()
        pizza_type = generate_random_pizza_type()
        rating = generate_random_rating()

        # Construct prompt with both Human and Assistant turns
        prompt = (f"\n\nHuman: Analyze customer feedback for pizza order. "
                  f"Customer says: {feedback_type}. "
                  f"Pizza type: {pizza_type}. "
                  f"Rating: {rating}"
                  f"\n\nAssistant: I'll help analyze this customer's pizza feedback.")

        entry = {
            "recordId": f"{i:03d}",
            "modelInput": {
                "prompt": prompt,
                "max_tokens_to_sample": 300,
                "temperature": 0.7
            },
            "metadata": {
                "customer_id": customer_id,
                "feedback": feedback_type,
                "pizza_type": pizza_type, 
                "rating": rating,
                "contact": {
                    "name": name,
                    "email": generate_random_email(name),
                    "phone": generate_random_phone()
                }
            }
        }
        entries.append(entry)
    
    return entries

def save_to_jsonl(entries, filename):
    with open(filename, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

# Generate 100 entries and save to a file
claude_batch_entries = generate_claude_batch_entries(10)
save_to_jsonl(claude_batch_entries, 'claude_batch_input.jsonl')

print(f"Generated {len(claude_batch_entries)} entries and saved to claude_batch_input.jsonl")