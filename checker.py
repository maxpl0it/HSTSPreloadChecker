import requests, json

js = ""
for line in requests.get("https://cs.chromium.org/codesearch/f/chromium/src/net/http/transport_security_state_static.json").text.split("\n"): # Get badly formatted JSON
    for i in range(len(line)): # Parse the line character by character (Definitely a performance bottleneck)
        if line[i] not in [" ", "\t"]: # Strip the initial padding
            break
    if line[i:i+2] == "//" or len(line[i:]) == 0: # Remove comment lines
        continue
    js += line[i:] # Add to formatted json
js = json.loads(js) # Parse JSON
subdomains_protected = [entry['name'].lower() for entry in js['entries'] if ('include_subdomains' in entry and entry['include_subdomains']) and 'mode' in entry and entry['mode'] == "force-https"] # Get all subdomains
subdomains_unprotected = [entry['name'].lower() for entry in js['entries'] if ('include_subdomains' not in entry or not entry['include_subdomains']) and 'mode' in entry and entry['mode'] == "force-https"] # if force-https is not in there, there's still an initial HTTP request.
while 1:
    domain = raw_input("[?] Enter base domain (e.g. google.com, facebook.com, ...): ").lower()
    subdomain = raw_input("[?] Enter subdomain (e.g. support, beta, beta.admin, or leave blank): ").lower()
    complete = (subdomain + "." if subdomain != "" else "") + domain # Attach subdomain and root domain
    if complete not in subdomains_unprotected and len(set(['.'.join(subdomain.split(".")[i:]) + "." + domain for i in range(len(subdomain.split(".")))] + [domain]) & set(subdomains_protected)) == 0: # Checking that nothing higher up on the tree protects all below.
        print("[-] %s is unprotected...\n" % complete)
    else:
        print("[+] %s is protected!\n" % complete)
