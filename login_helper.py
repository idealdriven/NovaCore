import requests
import json
import sys

def try_login(email, password, base_url):
    """Try logging in with the given credentials to get an access token."""
    
    login_url = f"{base_url}/api/v1/owners/token"
    
    print(f"Login URL: {login_url}")
    
    # The API expects form data (OAuth2 standard), not JSON
    data = {
        "username": email,  # OAuth2 uses "username" field even for email
        "password": password
    }
    
    try:
        # Make the login request
        response = requests.post(login_url, data=data)
        response.raise_for_status()  # Raise exception for error status codes
        
        # Parse the response
        token_data = response.json()
        
        print(f"\n✅ LOGIN SUCCESSFUL! ✅")
        print(f"Access token: {token_data['access_token']}")
        print(f"Token type: {token_data['token_type']}")
        print("\nUse the above access token to authenticate with Atlas.")
        
        # Try getting owner info
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        
        me_response = requests.get(f"{base_url}/api/v1/owners/me", headers=headers)
        if me_response.status_code == 200:
            owner_data = me_response.json()
            print(f"\nOwner information:")
            print(f"Name: {owner_data.get('name')}")
            print(f"Email: {owner_data.get('email')}")
            print(f"ID: {owner_data.get('id')}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ LOGIN FAILED ❌")
        
        try:
            error_data = response.json()
            print(f"Error: {error_data.get('detail', 'Unknown error')}")
        except:
            print(f"Error: {str(e)}")
            
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR ❌")
        print(f"Unexpected error: {str(e)}")
        return False

def main():
    base_url = "https://atlas-api-4t8d.onrender.com"
    
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        print("=== Atlas Login Helper ===")
        email = input("Email: ")
        password = input("Password: ")
    
    print(f"\nAttempting to login with:")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print(f"API URL: {base_url}")
    
    try_login(email, password, base_url)
    
    # Show info about the Atlas web interface
    print("\nTo use the web interface, go to:")
    print(f"{base_url}/static/index.html")
    print("\nMake sure to use the email and password you just tried.")

if __name__ == "__main__":
    main() 