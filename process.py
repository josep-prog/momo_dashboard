import xml.etree.ElementTree as ET
from datetime import datetime
import re
from db import init_db, store_data

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return [sms.attrib for sms in root.findall('sms')]

def standardize_name(name):
    if not name:
        return None
    
    # Convert to title case (e.g., "john doe" -> "John Doe")
    name = name.title()
    
    # Remove any characters that are not letters, spaces, periods, or hyphens
    name = re.sub(r'[^a-zA-Z\s\.\-]', '', name)
    
    # Remove extra whitespace and strip leading/trailing spaces
    name = ' '.join(name.split()).strip()
    
    # Remove common prefixes (if they somehow survived)
    name = re.sub(r'^(Mr|Mrs|Ms|Dr)\s+', '', name, flags=re.IGNORECASE)
    
    # Remove common transaction-related phrases
    name = re.sub(r'\s*(?:Has Been Completed|At|From|To|By|Ref|Txn|ID|Code|Rwf|Account|Transaction|Payment|Deposit|Transfer|Airtime|Cash|Power|Agent|MTN|Momo|Withdraw|Balance|Fee|Bank)\s*.*$', '', name, flags=re.IGNORECASE)
    
    # Remove any trailing numbers
    name = re.sub(r'\s*\d+.*$', '', name)
    
    # Ensure proper capitalization for company names with Ltd/LLC/etc
    name = re.sub(r'\b(Ltd|LLC|Inc|Corp|Co)\b', lambda m: m.group(1).upper(), name, flags=re.IGNORECASE)
    
    # Remove any remaining common words that shouldn't be part of names
    name = re.sub(r'\b(And|The|Of|For|On|In|At|To|By|From|With)\b', '', name, flags=re.IGNORECASE)
    
    # Clean up any resulting double spaces
    name = ' '.join(name.split())
    
    return name if name else None

def extract_name(body):
    if not body:
        return None
    
    # First try to extract company names
    company_pattern = r'(?:from|to|by)\s+([A-Za-z\s\.\-]+?(?:Ltd|LLC|Inc|Corp|Co)\b)'
    company_match = re.search(company_pattern, body, re.IGNORECASE)
    if company_match:
        name = company_match.group(1).strip()
        return standardize_name(name)
    
    # Then try to extract personal names (1-2 words)
    personal_pattern = r'(?:from|to|by|transferred to|received from)\s+([A-Za-z\s\.\-]+?)(?:\s*\d|\s*,|\s+at|\s+Has Been Completed|\s+Ref:|\s+Txn:|\s+ID:|\s+Code:|\s*\(|\.|\s*Rwf|\s*Account|\s*Transaction|\s*Payment|\s*Deposit|\s*Transfer|\s*Airtime|\s*Cash|\s*Power|\s*Agent|\s*MTN|\s*Momo|\s*Withdraw|\s*Balance|\s*Fee|\s*Bank|$)'
    personal_match = re.search(personal_pattern, body, re.IGNORECASE)
    if personal_match:
        name = personal_match.group(1).strip()
        standardized = standardize_name(name)
        # Only return if it's 1-2 words
        if standardized and 1 <= len(standardized.split()) <= 2:
            return standardized
    
    return None

def categorize_transaction(body):
    body = body.lower()
    if "received" in body and "rwf from" in body:
        return "incoming"
    elif "payment of" in body and "to" in body:
        return "payment"
    elif "transferred to" in body:
        return "transfer"
    elif "bank deposit" in body:
        return "deposit"
    elif "airtime" in body:
        return "airtime"
    elif "cash power" in body:
        return "cash_power"
    elif "withdrawn" in body and "agent" in body:
        return "withdrawal"
    else:
        return "other"

def extract_amount(body):
    match = re.search(r'(\d{1,3}(?:,?\d{3})*) RWF', body)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def extract_date(timestamp):
    return datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')

def process_data(sms_list):
    processed = []
    for sms in sms_list:
        body = sms['body']
        name = extract_name(body)
        processed.append({
            'type': categorize_transaction(body),
            'amount': extract_amount(body),
            'date': extract_date(sms['date']),
            'body': body,
            'address': sms['address'],
            'readable_date': sms['readable_date'],
            'name': name
        })
    return processed

def main():
    init_db()
    sms_data = parse_xml('modified_sms_v2.xml')
    processed = process_data(sms_data)
    store_data(processed)

if __name__ == '__main__':
    main()
