import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import json
load_dotenv()

def send_pushover_notification(message, title="Notification"):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": os.getenv("PUSHOVER_API_TOKEN"),
        "user": os.getenv("PUSHOVER_USER_KEY"), 
        "message": message,
        "title": title
    }
    response = requests.post(url, data=data)
    result = response.json()

    # Check if it worked
    if response.status_code == 200 and result.get('status') == 1:
        print(f"✓ Notification sent successfully!")
        print(f"Request ID: {result.get('request')}")
        return True
    else:
        print(f"✗ Failed to send notification")
        print(f"Status Code: {response.status_code}")
        print(f"Error: {result.get('errors', 'Unknown error')}")
        return False
    
def send_approval_notification(order_id, customer_name, amount):
    url = "https://api.pushover.net/1/messages.json"
    
    timestamp = datetime.now().isoformat()
    
    actions = [
        {
            "action": f"approve_{order_id}",
            "label": "✓ Approve Order",
            "url": f"https://your-api.com/orders/{order_id}/approve",
            "method": "POST",
            "content": json.dumps({
                "order_id": order_id,
                "action": "approved",
                "timestamp": timestamp,
                "via": "pushover"
            }),
            "content_type": "application/json"
        },
        {
            "action": f"deny_{order_id}",
            "label": "✗ Deny Order",
            "url": f"https://your-api.com/orders/{order_id}/deny",
            "method": "POST",
            "content": json.dumps({
                "order_id": order_id,
                "action": "denied",
                "timestamp": timestamp,
                "via": "pushover"
            }),
            "content_type": "application/json"
        },
        {
            "action": f"review_{order_id}",
            "label": "📋 Review Later",
            "url": f"https://your-api.com/orders/{order_id}/review-later",
            "method": "PUT",
            "content": json.dumps({
                "order_id": order_id,
                "snooze_until": "2025-10-06T09:00:00"
            })
        }
    ]
    
    data = {
        "token": os.getenv("PUSHOVER_API_TOKEN"),
        "user": os.getenv("PUSHOVER_USER_KEY"), 
        "title": "🔔 Order Approval Required",
        "message": f"Order #{order_id}\nCustomer: {customer_name}\nAmount: ${amount}\n\nPlease review and approve or deny.",
        "actions": json.dumps(actions),
        "priority": 1,  # High priority
        "sound": "cashregister",
        "url": f"https://your-dashboard.com/orders/{order_id}",
        "url_title": "View Order Details"
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    
    if response.status_code == 200:
        print(f"✓ Approval notification sent for order {order_id}")
        print(f"Request ID: {result.get('request')}")
        return True
    else:
        print(f"✗ Failed to send notification: {result.get('errors')}")
        return False

def debug_pushover_notification():
    actions = [
        {
            "action": "approve",
            "label": "Approve",
            "url": "https://httpbin.org/post",  # Test endpoint
            "method": "POST",
            "content": json.dumps({"test": "data"})
        }
    ]
    
    data = {
        "token": os.getenv("PUSHOVER_API_TOKEN"),
        "user": os.getenv("PUSHOVER_USER_KEY"), 
        "message": "Debug test - check for buttons below",
        "title": "Debug Test",
        "actions": json.dumps(actions)
    }
    
    # Print what you're sending
    print("Sending data:")
    print(json.dumps(data, indent=2))
    
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    
    # Print response
    print("\nPushover response:")
    print(json.dumps(response.json(), indent=2))
    
def send_emergency_notification_with_actions():
    url = "https://api.pushover.net/1/messages.json"
    
    actions = [
        {
            "action": "acknowledge",
            "label": "Acknowledge",
            "url": "https://your-api.com/acknowledge",
            "method": "POST"
        },
                {
            "action": "approve",
            "label": "Approve",
            "url": "https://httpbin.org/post",  # Test endpoint
            "method": "POST",
            "content": json.dumps({"test": "data"})
        }
    ]
    
    data = {
        "token": os.getenv("PUSHOVER_API_TOKEN"),
        "user": os.getenv("PUSHOVER_USER_KEY"), 
        "message": "URGENT: Server is down!",
        "title": "Critical Alert",
        "priority": 2,  # Emergency priority
        "retry": 60,    # Retry every 60 seconds
        "expire": 3600, # Expire after 1 hour
        "actions": json.dumps(actions)
    }
    
    response = requests.post(url, data=data)
    return response.json()

if __name__ == '__main__':
    debug_pushover_notification()