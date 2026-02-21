import os
import sys
import signal
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, PairStatus
from neonize.types import JID

# --- CONFIGURATION ---
# The session name. It will save your login credentials here.
SESSION_NAME = "omega_session.sqlite3"

# Initialize the client
client = NewClient(SESSION_NAME)

# Global variable to store allowed contacts
allowed_contacts = set()

def signal_handler(sig, frame):
    print("\n[!] Omega Pro MSJ shutting down. Stay dangerous.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@client.event(ConnectedEv)
def on_connected(client, event: ConnectedEv):
    print("[+] Connection established to WhatsApp servers.")
    print("[+] Fetching contact list... this might take a second.")
    
    # Fetch all contacts and store their JIDs (phone numbers)
    contacts = client.get_contacts()
    for contact in contacts:
        allowed_contacts.add(contact.Jid.User)
    
    print(f"[+] Whitelisted {len(allowed_contacts)} contacts. Everyone else gets the hammer.")

@client.event(PairStatus)
def on_pair_status(client, status: PairStatus):
    print(f"[*] Pairing Status: {status}")
    if status == PairStatus.PAIRED:
        print("[+] Logged in successfully.")

@client.event(MessageEv)
def on_message(client, message: MessageEv):
    # Ignore messages from yourself
    if message.Info.IsFromMe:
        return

    # Extract sender details
    # The sender JID looks like '1234567890@s.whatsapp.net'
    sender_jid = message.Info.Sender
    sender_number = sender_jid.User
    
    # Check if the sender is a group (usually ends in g.us)
    # If you want to block unknown groups too, remove this check.
    if "g.us" in sender_jid.Server:
        return

    # THE KILL SWITCH 💀
    if sender_number not in allowed_contacts:
        print(f"[!] UNKNOWN DETECTED: {sender_number}")
        print(f"[*] Executing Block Protocol on {sender_number}...")
        
        try:
            # Send a final goodbye message (Optional - delete if you want stealth)
            # client.send_message(sender_jid, "🚫 Access Denied. You are not in the whitelist.")
            
            # BLOCK THE USER
            # Note: The exact block method depends on the library version updates, 
            # but usually modifying the privacy settings or using a block action works.
            # In raw protocol, we send a block request.
            
            client.update_blocklist(sender_jid, action="block")
            print(f"[+] {sender_number} has been BLOCKED successfully.")
            
        except Exception as e:
            print(f"[ERROR] Failed to block {sender_number}: {e}")
    else:
        print(f"[ok] Message from contact: {sender_number}")

if __name__ == "__main__":
    print("[-] Omega Pro MSJ: Initializing...")
    print("[-] Scan the QR code if prompted.")
    client.connect()
