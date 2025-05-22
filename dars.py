import random
import re
import string
import time
import uuid
import requests

# Generate a fake UNIX timestamp (e.g., last few days)
def generate_fake_timestamp():
    now = int(time.time())
    random_offset = random.randint(-86400 * 1, 0)  # Up to 1 day ago
    return str(now + random_offset)

# Generate a random fake IPv4 address
def generate_fake_ip():
    return "{}.{}.{}.{}".format(
        random.randint(1, 254),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(1, 254)
    )

# Base headers (without IP and timestamp)
base_headers = {
    'authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
    'User-Agent': '[FBAN/FB4A;FBAV/388.0.0.21.107;FBBV/469533592;FBDM/{density=2.0,width=720,height=1520};FBLC/en_US;FBRV/0;FBCR/;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.lite;FBDV/SM-A107F;FBSV/10;FBOP/1;FBCA/armeabi-v7a:armeabi]',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "X-FB-Net-HNI": "51502",  # Smart PH
    "X-FB-SIM-HNI": "51502",
    "X-FB-HTTP-Engine": "Liger",
    "Accept-Language": "en-US,en;q=0.5",
    'x-fb-friendly-name': 'Authenticate',
    'x-fb-connection-type': 'Unknown',
    'accept-encoding': 'gzip, deflate',
    'content-type': 'application/x-www-form-urlencoded',
    'x-fb-http-engine': 'Liger',
}

# Parse line into email and password
def parse_line(line):
    fb_prefix = "https://www.facebook.com/profile.php?id="
    if line.startswith(fb_prefix):
        line = line[len(fb_prefix):]

    match = re.match(r'\s*([^:\|\t ]+)\s*[:\|\t ]\s*(.+)', line)
    if match:
        email_or_link = match.group(1).strip()
        password = match.group(2).strip()
        return email_or_link, password
    return None, None

def main():
    with open("tokens.txt", "w", encoding="utf-8") as token_file:
        while True:
            line = input("Enter email password: ").strip()
            if line.lower() == 'exit':
                break

            email, password = parse_line(line)
            if not email or not password:
                print("\033[91m[!] Invalid format. Example: email|password or https://www.facebook.com/profile.php?id=123456789 | password\033[0m")
                continue

            data = {
                'email': email,
                'password': password,
                'credentials_type': 'password',
                'adid': ''.join(random.choices(string.hexdigits, k=16)),
                'format': 'json',
                'device_id': str(uuid.uuid4()),
                'generate_analytics_claims': '0',
                'source': 'login',
                'error_detail_type': 'button_with_disabled',
                'enroll_misauth': 'false',
                'generate_session_cookies': '0',
                'generate_machine_id': '0',
                'fb_api_req_friendly_name': 'authenticate',
            }

            # Generate new fake IP and timestamp for each request
            fake_ip = generate_fake_ip()

            # Copy base headers so you don't modify the original dict
            headers = base_headers.copy()
            headers['X-Forwarded-For'] = fake_ip
            headers['Client-IP'] = fake_ip
            headers['x-fb-request-time'] = generate_fake_timestamp()

            try:
                response = requests.post('https://b-graph.facebook.com/auth/login', headers=headers, data=data)
                try:
                    result = response.json()
                except Exception:
                    print(f"\033[91m[!] Failed to parse JSON. Raw response:\033[0m\n{response.text}")
                    continue

                if 'access_token' in result:
                    token = result['access_token']
                    print(f"\033[92mtoken: {token}\033[0m")
                    token_file.write(f"{email} {password} | {token}\n")
                elif 'error' in result:
                    error = result['error']
                    user_msg = error.get('error_user_msg', error.get('message', str(error)))
                    print(f"\033[91m[-] {email} {password} | {user_msg}\033[0m")
                else:
                    print(f"\033[93m[?] {email} {password} | Unexpected response: {result}\033[0m")
            except Exception as e:
                print(f"\033[91m[!] {email} {password} | Exception: {e}\033[0m")
                if 'response' in locals():
                    print(f"Response text: {response.text}")
                else:
                    print("No response")

if __name__ == "__main__":
    main()
