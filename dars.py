import random
import re
import string
import uuid

import requests

headers = {
    'authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.7103.60 Mobile Safari/537.36 [FBAN/com.facebook.lite;FBLC/pt_PT;FBAV/377.0.0.6.104;FBCX/modulariab;]',
    # 'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-A107F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.136 Mobile Safari/537.36 [FBAN/Orca-Android; FBAV/367.0.0.5.109;]',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://m.facebook.com/",
    "Connection": "keep-alive",
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

# Extract email and password from each line
def parse_line(line):
    # Use regex to split on the first occurrence of any separator including multiple spaces/tabs
    match = re.match(r'\s*([^:\|\t ]+)\s*[:\|\t ]\s*(.+)', line)
    if match:
        email = match.group(1).strip()
        password = match.group(2).strip()
        return email, password
    return None, None

# Main login and token saving logic
def main():
    with open("tokens.txt", "w", encoding="utf-8") as token_file:
        while True:
            line = input("Enter email and password: ").strip()
            if line.lower() == 'exit':
                print("Exiting...")
                break
            email, password = parse_line(line)
            if not email or not password:
                print("\033[91m[!] Invalid format. Example: email|password\033[0m")
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

            try:
                response = requests.post('https://b-graph.facebook.com/auth/login', headers=headers, data=data)
                result = response.json()
                if 'access_token' in result:
                    token = result['access_token']
                    print(f"\033[92m[+] {email} {password} | Access token: {token}\033[0m")
                    token_file.write(f"{email} {password} | {token}\n")
                elif 'error' in result:
                    if 'error_user_msg' in result['error']:
                        print(f"\033[91m[-] {email} {password} | {result['error']['error_user_msg']}\033[0m")
                    else:
                        print(f"\033[91m[-] {email} {password} | Error: {result['error']}\033[0m")
                else:
                    print(f"\033[93m[?] {email} {password} | Unexpected response: {result}\033[0m")
            except Exception as e:
                print(f"\033[91m[!] {email} {password} | Exception: {e}\033[0m")
                print(f"Response text: {response.text if 'response' in locals() else 'No response'}")

if __name__ == "__main__":
    main()
