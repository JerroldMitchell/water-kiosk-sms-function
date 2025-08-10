import json
import os
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error

# Configuration Constants - Environment Variables with Fallbacks
APPWRITE_PROJECT_ID = os.environ.get('APPWRITE_PROJECT_ID', '689107c288885e90c039')
APPWRITE_DATABASE_ID = os.environ.get('APPWRITE_DATABASE_ID', '6864aed388d20c69a461')
APPWRITE_API_KEY = os.environ.get('APPWRITE_API_KEY', '0f3a08c2c4fc98480980cbe59cd2db6b8522734081f42db3480ab2e7a8ffd7c46e8476a62257e429ff11c1d6616e814ae8753fb07e7058d1b669c641012941092ddcd585df802eb2313bfba49bf3ec3f776f529c09a7f5efef2988e4b4821244bbd25b3cd16669885c173ac023b5b8a90e4801f3584eef607506362c6ae01c94')
CUSTOMERS_COLLECTION_ID = os.environ.get('CUSTOMERS_COLLECTION_ID', 'customers')
APPWRITE_ENDPOINT = os.environ.get('APPWRITE_ENDPOINT', 'http://appwrite-traefik/v1')

def main(context):
    """
    Water Kiosk SMS System - Clean Modern Version
    """
    try:
        # Handle payload parsing - fix for string body issue
        raw_body = context.req.body or {}
        method = context.req.method
        
        # Parse body if it's a JSON string
        if isinstance(raw_body, str):
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                body = {}
        else:
            body = raw_body
        
        # Debug logging
        context.log(f"Method: {method}")
        context.log(f"Raw body: {raw_body}")
        context.log(f"Raw body type: {type(raw_body)}")
        context.log(f"Parsed body: {body}")
        context.log(f"Headers: {getattr(context.req, 'headers', {})}")
        
        if method == 'GET':
            return context.res.json({
                'status': 'Water Kiosk SMS System Active',
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'endpoints': {
                    'status': 'GET / - This status page',
                    'test_database': 'POST {"action": "test_database"}',
                    'test_sms': 'POST {"action": "test_sms", "phone": "+254700000000"}',
                    'simulate_sms': 'POST {"action": "simulate_sms", "from": "+254700000000", "text": "REGISTER"}',
                    'webhook': 'POST with SMS data from Africa\'s Talking'
                }
            })
        
        elif method == 'POST':
            action = body.get('action')
            
            if action == 'test_database':
                return context.res.json(test_database_connection(context))
            
            elif action == 'test_sms':
                phone = body.get('phone', '+254700000001')
                result = send_sms(context, phone, 'Test SMS from Tusafishe Water Kiosk! 💧')
                return context.res.json(result)
            
            elif action == 'simulate_sms':
                phone = body.get('from', '+254700000000')
                text = body.get('text', 'REGISTER')
                result = handle_sms(context, phone, text, is_real=False)
                return context.res.json(result)
            
            # Handle real SMS webhook from Africa's Talking
            elif 'from' in body and 'text' in body:
                phone = body.get('from')
                text = body.get('text', '').strip()
                result = handle_sms(context, phone, text, is_real=True)
                return context.res.json(result)
            
            else:
                return context.res.json({
                    'error': 'Invalid request',
                    'received': body,
                    'help': 'Send SMS data with "from" and "text" fields'
                }, 400)
        
        else:
            return context.res.json({'error': f'Method {method} not allowed'}, 405)
        
    except Exception as e:
        context.error(f'Function error: {str(e)}')
        return context.res.json({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500)


def test_database_connection(context):
    """Test Appwrite database connection"""
    try:
        project_id = APPWRITE_PROJECT_ID
        database_id = APPWRITE_DATABASE_ID
        api_key = APPWRITE_API_KEY
        endpoint = APPWRITE_ENDPOINT
        
        if not all([project_id, database_id, api_key]):
            return {
                'success': False,
                'error': 'Missing environment variables',
                'required': ['APPWRITE_PROJECT_ID', 'APPWRITE_DATABASE_ID', 'APPWRITE_API_KEY']
            }
        
        url = f'{endpoint}/databases/{database_id}/collections'
        headers = {
            'X-Appwrite-Project': project_id,
            'X-Appwrite-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        context.log(f"✅ Database connected! Found {data['total']} collections")
        
        return {
            'success': True,
            'message': 'Database connection working!',
            'collections': data['total'],
            'collection_names': [col['name'] for col in data.get('collections', [])]
        }
        
    except Exception as e:
        context.error(f"Database test failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def send_sms(context, phone_number, message):
    """Send SMS via Africa's Talking"""
    try:
        api_key = os.environ.get('AFRICAS_TALKING_API_KEY')
        username = os.environ.get('AFRICAS_TALKING_USERNAME', 'sandbox')
        
        if not api_key:
            context.log(f"TEST MODE: Would send to {phone_number}: {message}")
            return {
                'success': True,
                'message': 'SMS logged in test mode',
                'test_mode': True
            }
        
        # Format phone number for Kenya
        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            else:
                phone_number = '+254' + phone_number
        
        url = "https://api.africastalking.com/version1/messaging"
        data = urllib.parse.urlencode({
            'username': username,
            'to': phone_number,
            'message': message
        }).encode('utf-8')
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apikey': api_key
        }
        
        request = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(request, timeout=15)
        result = json.loads(response.read().decode('utf-8'))
        
        context.log(f"✅ SMS sent to {phone_number}")
        return {
            'success': True,
            'sms_result': result,
            'test_mode': False
        }
        
    except Exception as e:
        context.error(f"SMS failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def handle_sms(context, phone_number, message, is_real=False):
    """Handle incoming SMS"""
    try:
        context.log(f"Processing {'REAL' if is_real else 'SIMULATED'} SMS from {phone_number}: {message}")
        
        # Get or create customer
        customer = get_customer(context, phone_number)
        if not customer:
            customer = create_customer(context, phone_number)
        
        # Process message and get response
        response_text = process_message(context, customer, message)
        
        # Send SMS response if real
        if is_real and response_text:
            sms_result = send_sms(context, phone_number, response_text)
        
        return {
            'success': True,
            'phone': phone_number,
            'received': message,
            'response': response_text,
            'customer_id': customer.get('$id') if customer else None,
            'is_real': is_real
        }
        
    except Exception as e:
        context.error(f'SMS handling error: {str(e)}')
        return {
            'success': False,
            'error': str(e)
        }


def get_customer(context, phone_number):
    """Get customer by phone number"""
    try:
        project_id = APPWRITE_PROJECT_ID
        database_id = APPWRITE_DATABASE_ID
        collection_id = CUSTOMERS_COLLECTION_ID
        api_key = APPWRITE_API_KEY
        endpoint = APPWRITE_ENDPOINT
        
        # Clean phone number
        clean_phone = phone_number.replace('+254', '0') if phone_number.startswith('+254') else phone_number
        
        query = f'equal("phone_number","{phone_number}")'
        url = f'{endpoint}/databases/{database_id}/collections/{collection_id}/documents?queries[]={urllib.parse.quote(query)}'
        
        headers = {
            'X-Appwrite-Project': project_id,
            'X-Appwrite-Key': api_key
        }
        
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('documents'):
            context.log(f"Found existing customer: {phone_number}")
            return data['documents'][0]
        
        context.log(f"No customer found for: {phone_number}")
        return None
        
    except Exception as e:
        context.error(f"Error getting customer: {str(e)}")
        return None


def create_customer(context, phone_number):
    """Create new customer"""
    try:
        project_id = APPWRITE_PROJECT_ID
        database_id = APPWRITE_DATABASE_ID
        collection_id = CUSTOMERS_COLLECTION_ID
        api_key = APPWRITE_API_KEY
        endpoint = APPWRITE_ENDPOINT
        
        url = f'{endpoint}/databases/{database_id}/collections/{collection_id}/documents'
        
        customer_data = {
            'documentId': 'unique()',
            'data': {
                'phone_number': phone_number,
                'created_at': datetime.now().isoformat(),
                'registration_state': 'new',  # Changed from 'state' to 'registration_state'
                'is_registered': False,
                'credits': 0
            }
        }
        
        headers = {
            'X-Appwrite-Project': project_id,
            'X-Appwrite-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(customer_data).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        context.log(f"✅ Created customer: {phone_number}")
        return result
        
    except Exception as e:
        context.error(f"Error creating customer: {str(e)}")
        return None


def update_customer(context, customer_id, updates):
    """Update customer data"""
    try:
        project_id = APPWRITE_PROJECT_ID
        database_id = APPWRITE_DATABASE_ID
        collection_id = CUSTOMERS_COLLECTION_ID
        api_key = APPWRITE_API_KEY
        endpoint = APPWRITE_ENDPOINT
        
        url = f'{endpoint}/databases/{database_id}/collections/{collection_id}/documents/{customer_id}'
        
        payload = {'data': updates}
        headers = {
            'X-Appwrite-Project': project_id,
            'X-Appwrite-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
        response = urllib.request.urlopen(request, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        context.log(f"✅ Updated customer: {customer_id}")
        return result
        
    except Exception as e:
        context.error(f"Error updating customer: {str(e)}")
        return None


def process_message(context, customer, message):
    """Process customer message and return response"""
    if not customer:
        return "Welcome to Tusafishe Water Kiosks! 💧\nReply REGISTER to start"
    
    state = customer.get('registration_state', 'new')  # Changed from 'state' to 'registration_state'
    msg = message.lower().strip()
    
    try:
        # Handle commands
        if msg in ['menu', 'help', 'start']:
            if customer.get('is_registered'):
                credits = customer.get('credits', 0)
                return (f"💧 Tusafishe Water Kiosk\n"
                       f"Balance: {credits} KES\n"
                       f"Commands: BALANCE, MENU")
            else:
                update_customer(context, customer['$id'], {'registration_state': 'main_menu'})
                return ("Welcome to Tusafishe! 💧\n"
                       "1. Register\n"
                       "2. Check Balance\n"
                       "Reply with number")
        
        elif msg in ['register', '1']:
            if customer.get('is_registered'):
                return "Already registered! Reply MENU for options"
            else:
                update_customer(context, customer['$id'], {'registration_state': 'registration_id'})
                return "Let's register! Enter your ID number:"
        
        elif state == 'registration_id':
            if len(message) >= 6:
                # Just update the state, don't save id_number since it doesn't exist in schema
                update_customer(context, customer['$id'], {
                    'registration_state': 'registration_name'
                })
                return "✅ ID saved! Enter your full name:"
            else:
                return "Please enter valid ID (min 6 digits):"
        
        elif state == 'registration_name':
            update_customer(context, customer['$id'], {
                'full_name': message,
                'registration_state': 'registration_location'
            })
            return "✅ Name saved! Enter your location:"
        
        elif state == 'registration_location':
            account_id = f"TSF{customer['$id'][-6:].upper()}"
            update_customer(context, customer['$id'], {
                'location': message,
                'account_id': account_id,
                'is_registered': True,
                'registration_state': 'completed'
            })
            return (f"🎉 Registration complete!\n"
                   f"Account: {account_id}\n"
                   f"Reply MENU for options")
        
        elif msg in ['balance', '2']:
            if customer.get('is_registered'):
                credits = customer.get('credits', 0)
                account = customer.get('account_id', 'N/A')
                return f"💧 Account: {account}\nBalance: {credits} KES"
            else:
                return "Please register first. Reply REGISTER"
        
        else:
            if customer.get('is_registered'):
                return "Command not recognized. Reply MENU for help"
            else:
                return "Welcome! Reply REGISTER to start"
    
    except Exception as e:
        context.error(f'Message processing error: {str(e)}')
        return "Error occurred. Reply MENU to try again"
