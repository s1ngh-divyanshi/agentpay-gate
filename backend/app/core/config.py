import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SPEND_LIMIT_MAX_PER_TX_INR = float(os.getenv("SPEND_LIMIT_MAX_PER_TX_INR", 5000.0))

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))