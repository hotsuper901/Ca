import os
import sys
import signal
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, PairStatusEv

# --- CONFIGURATION ---
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
    
    contacts = client.get_contacts()
    for contact in contacts:
        try:
            if hasattr(contact, 'JID'):
                allowed_contacts.add(contact.JID.User)
            elif hasattr(contact, 'User'):
                allowed_contacts.add(contact.User)
            elif hasattr(contact, 'jid'):
                allowed_contacts.add(contact.jid.User)
        except Exception as e:
            print(f"Error processing contact: {e}")
            continue
    
    print(f"[+] Whitelisted {len(allowed_contacts)} contacts.")

@client.event(PairStatusEv)
def on_pair_status(client, status: PairStatusEv):
    print(f"[*] Pairing Status: {status}")

@client.event(MessageEv)
def on_message(client, message: MessageEv):
    if message.Info.IsFromMe:
        return

    try:
        if hasattr(message.Info, 'Sender') and hasattr(message.Info.Sender, 'User'):
            sender_number = message.Info.Sender.User
        elif hasattr(message.Info, 'Sender') and hasattr(message.Info.Sender, 'user'):
            sender_number = message.Info.Sender.user
        elif hasattr(message, 'Sender') and hasattr(message.Sender, 'User'):
            sender_number = message.Sender.User
        else:
            return
        
        sender_server = message.Info.Sender.Server if hasattr(message.Info.Sender, 'Server') else ""
        if "g.us" in sender_server:
            return

        if sender_number not in allowed_contacts:
            print(f"[!] UNKNOWN DETECTED: {sender_number}")
            print(f"[*] Executing Block Protocol on {sender_number}...")
            
            try:
                if hasattr(client, 'block_user'):
                    client.block_user(message.Info.Sender)
                    print(f"[+] {sender_number} has been BLOCKED successfully.")
                elif hasattr(client, 'update_blocklist'):
                    client.update_blocklist(message.Info.Sender, action="block")
                    print(f"[+] {sender_number} has been BLOCKED successfully.")
                else:
                    print(f"[!] No block method found.")
            except Exception as e:
                print(f"[ERROR] Failed to block {sender_number}: {e}")
        else:
            print(f"[ok] Message from contact: {sender_number}")
            
    except Exception as e:
        print(f"[ERROR] Processing message: {e}")

if __name__ == "__main__":
    print("[-] Omega Pro MSJ: Initializing...")
    print("[-] Scan the QR code if prompted.")
    client.connect()                allowed_contacts.add(contact.JID.User)
            elif hasattr(contact, 'User'):
                allowed_contacts.add(contact.User)
            elif hasattr(contact, 'jid'):
                allowed_contacts.add(contact.jid.User)
            else:
                # Print contact structure for debugging
                print(f"Contact structure: {dir(contact)}")
                print(f"Contact: {contact}")
        except Exception as e:
            print(f"Error processing contact: {e}")
            continue
    
    print(f"[+] Whitelisted {len(allowed_contacts)} contacts. Everyone else gets the hammer.")

@client.event(PairStatusEv)
def on_pair_status(client, status: PairStatusEv):
    print(f"[*] Pairing Status: {status}")

@client.event(MessageEv)
def on_message(client, message: MessageEv):
    # Ignore messages from yourself
    if message.Info.IsFromMe:
        return

    # Extract sender details
    try:
        # Try different ways to access sender number
        if hasattr(message.Info, 'Sender') and hasattr(message.Info.Sender, 'User'):
            sender_number = message.Info.Sender.User
        elif hasattr(message.Info, 'Sender') and hasattr(message.Info.Sender, 'user'):
            sender_number = message.Info.Sender.user
        elif hasattr(message, 'Sender') and hasattr(message.Sender, 'User'):
            sender_number = message.Sender.User
        else:
            print(f"Message structure: {dir(message.Info)}")
            print(f"Sender info: {message.Info.Sender if hasattr(message.Info, 'Sender') else 'No sender'}")
            return
        
        # Check if the sender is a group (usually ends in g.us)
        sender_server = message.Info.Sender.Server if hasattr(message.Info.Sender, 'Server') else ""
        if "g.us" in sender_server:
            return

        # THE KILL SWITCH 💀
        if sender_number not in allowed_contacts:
            print(f"[!] UNKNOWN DETECTED: {sender_number}")
            print(f"[*] Executing Block Protocol on {sender_number}...")
            
            try:
                # Try different block methods
                if hasattr(client, 'block_user'):
                    client.block_user(message.Info.Sender)
                    print(f"[+] {sender_number} has been BLOCKED successfully using block_user.")
                elif hasattr(client, 'update_blocklist'):
                    client.update_blocklist(message.Info.Sender, action="block")
                    print(f"[+] {sender_number} has been BLOCKED successfully using update_blocklist.")
                else:
                    print(f"[!] No block method found. Available methods: {dir(client)}")
                    
            except Exception as e:
                print(f"[ERROR] Failed to block {sender_number}: {e}")
        else:
            print(f"[ok] Message from contact: {sender_number}")
            
    except Exception as e:
        print(f"[ERROR] Processing message: {e}")

if __name__ == "__main__":
    print("[-] Omega Pro MSJ: Initializing...")
    print("[-] Scan the QR code if prompted.")
    client.connect()def on_pair_status(client, status: PairStatusEv):  # Changed to PairStatusEv
    print(f"[*] Pairing Status: {status}")
    # Note: You might need to check the actual status value/type
    # if status == PairStatusEv.PAIRED:  # Adjust this based on actual implementation
    #     print("[+] Logged in successfully.")

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
            # Note: Check the correct method name for blocking in your neonize version
            # Some possibilities:
            # client.block_user(sender_jid)
            # or
            client.update_blocklist(sender_jid, action="block")
            print(f"[+] {sender_number} has been BLOCKED successfully.")
            
        except Exception as e:
            print(f"[ERROR] Failed to block {sender_number}: {e}")
    else:
        print(f"[ok] Message from contact: {sender_number}")

if __name__ == "__main__":
    print("[-] Omega Pro MSJ: Initializing...")
    print("[-] Scan the QR code if prompted.")
    client.connect()def on_pair_status(client, status: PairStatus):
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
