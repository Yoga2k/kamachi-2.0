"""
payment_gateway.py - YOUPI PG Integration for KAMACHI AI 2.0
Enables voice-driven UPI payments, dynamic checkout generation, and real-time status verification.
"""

import re
import json
import uuid
import webbrowser
import urllib.request
import urllib.error
from utils import speak, take_command

YOUPI_API_BASE = "http://localhost:6100"

def extract_amount(text):
    """Extract numeric payment amount from text/voice command."""
    if not text:
        return None
    # Match patterns like: 500, 500.50, 1000 rupees, Rs 500, Rs. 500
    match = re.search(r'(?:rs\.?|rupees|inr)?\s*(\d+(?:\.\d{1,2})?)\s*(?:rs\.?|rupees|inr)?', text, re.IGNORECASE)
    if match:
        try:
            val = float(match.group(1))
            if val > 0:
                return val
        except ValueError:
            pass
    return None

def create_payment_session(amount, order_id=None, note="Kamachi AI Payment"):
    """
    Create a payment session via YOUPI PG REST API.
    Returns the session dict containing paymentId, checkoutUrl, status, etc.
    """
    if not order_id:
        order_id = f"KAMACHI-{uuid.uuid4().hex[:8].upper()}"

    url = f"{YOUPI_API_BASE}/api/v1/payments"
    payload = {
        "orderId": order_id,
        "amount": float(amount),
        "currency": "INR",
        "metadata": {
            "source": "kamachi_assistant",
            "note": note
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {"success": True, "data": data}
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8")
        try:
            err_json = json.loads(err_msg)
            return {"success": False, "error": err_json.get("error", str(err))}
        except Exception:
            return {"success": False, "error": f"HTTP {err.code}: {err.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_payment_status(payment_id):
    """Fetch live status of a payment session from YOUPI PG."""
    url = f"{YOUPI_API_BASE}/api/v1/payments/{payment_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Cache last payment ID for quick status inquiries
_last_payment_id = None

def voice_payment_control(command):
    """
    Handle voice commands for payment operations:
    - 'make a payment of 500 rupees'
    - 'pay 200'
    - 'create upi payment'
    - 'check payment status'
    """
    global _last_payment_id
    cmd = command.lower() if command else ""

    # Check status of last payment
    if any(k in cmd for k in ["payment status", "check payment", "verify payment", "is payment done"]):
        if not _last_payment_id:
            speak("No recent payment session found to check.")
            return
        speak("Checking status with YOUPI payment gateway...")
        res = get_payment_status(_last_payment_id)
        if res.get("success"):
            status = res["data"].get("status", "UNKNOWN")
            amount = res["data"].get("amount", "")
            if status in ["SUCCESS", "OBSERVED_SUCCESS", "RECONCILED"]:
                speak(f"Great news! Payment of {amount} rupees has been successfully verified.")
            elif status == "INITIATED":
                speak(f"The payment session for {amount} rupees is open and awaiting scanning.")
            elif status == "ACTIVE":
                speak(f"The payment session is active on the UPI network.")
            elif status in ["EXPIRED", "FAILED"]:
                speak(f"The payment of {amount} rupees has expired or failed.")
            else:
                speak(f"Current payment status is {status}.")
        else:
            speak(f"Could not retrieve status: {res.get('error')}")
        return

    # Initiate payment flow
    amount = extract_amount(cmd)
    if not amount:
        speak("How much amount would you like to pay in rupees?")
        amount_input = take_command("Say the amount in rupees (e.g., 100):")
        amount = extract_amount(amount_input)

    if not amount or amount <= 0:
        speak("Invalid payment amount. Payment request cancelled.")
        return

    speak(f"Initiating payment of {int(amount) if amount.is_integer() else amount} rupees on YOUPI Gateway...")
    result = create_payment_session(amount=amount)

    if result.get("success"):
        data = result["data"]
        _last_payment_id = data.get("paymentId")
        checkout_url = data.get("checkoutUrl")

        speak(f"Payment gateway ready. Opening checkout in your browser now.")
        if checkout_url:
            webbrowser.open(checkout_url)
            print(f"[KAMACHI Payment] Checkout URL: {checkout_url}")
            print(f"[KAMACHI Payment] Payment ID: {_last_payment_id}")
    else:
        err = result.get("error", "Unknown error")
        speak(f"Sorry, could not create payment session. {err}")
        print(f"[KAMACHI Payment Error] {err}")
