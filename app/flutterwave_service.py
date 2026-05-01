"""
Flutterwave Payment Integration Service
"""
import requests
import os
from typing import Optional, Dict
from datetime import datetime

class FlutterwaveService:
    """Service for handling Flutterwave payments"""
    
    def __init__(self):
        self.secret_key = os.getenv("FLUTTERWAVE_SECRET_KEY", "FLWSECK-f85cc6b5549a25f650594873b264a445-19de5373a8bvt-X").strip()
        self.public_key = os.getenv("FLUTTERWAVE_PUBLIC_KEY", "FLWPUBK-aadd64c0ee68f34f45e180602733d9db-X").strip()
        self.base_url = "https://api.flutterwave.com/v3"
        self.encryption_key = os.getenv("FLUTTERWAVE_ENCRYPTION_KEY", "f85cc6b5549a68c339483599").strip()
    
    def initialize_payment(
        self,
        amount: float,
        email: str,
        phone: str,
        name: str,
        tx_ref: str,
        redirect_url: str = "",
        currency: str = "NGN"
    ) -> Dict:
        """
        Initialize a payment with Flutterwave
        
        Args:
            amount: Amount to charge
            email: Customer email
            phone: Customer phone
            name: Customer name
            tx_ref: Unique transaction reference
            redirect_url: URL to redirect after payment
            currency: Currency code (default: NGN)
        
        Returns:
            Dict with payment link and reference
        """
        
        url = f"{self.base_url}/payments"
        
        print(f"🔵 Flutterwave payment initialization:")
        print(f"  - URL: {url}")
        print(f"  - Amount: {amount}")
        print(f"  - Email: {email}")
        print(f"  - Phone: {phone}")
        print(f"  - Name: {name}")
        print(f"  - TX Ref: {tx_ref}")
        print(f"  - Secret Key: {self.secret_key[:20]}...")
        
        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": currency,
            "redirect_url": redirect_url or "https://your-app.com/payment/callback",
            "payment_options": "card,banktransfer,ussd",
            "customer": {
                "email": email,
                "phonenumber": phone,
                "name": name
            },
            "customizations": {
                "title": "Eagle's Pride",
                "description": "Subscription payment for Eagle's Pride",
                "logo": "https://jobnect-backend.onrender.com/static/logo.png"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"🔵 Making Flutterwave API call to: {url}")
            print(f"🔵 Payload: {payload}")
            print(f"🔵 Headers: {headers}")
            
            response = requests.post(url, json=payload, headers=headers)
            print(f"🔵 Response status: {response.status_code}")
            print(f"🔵 Response body: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                payment_link = data["data"]["link"]
                print(f"🔵 Flutterwave payment link: {payment_link}")
                return {
                    "success": True,
                    "payment_link": payment_link,
                    "tx_ref": tx_ref,
                    "message": "Payment initialized successfully"
                }
            else:
                error_msg = data.get("message", "Failed to initialize payment")
                print(f"🔴 Flutterwave API error: {error_msg}")
                return {
                    "success": False,
                    "message": error_msg
                }
        
        except requests.exceptions.RequestException as e:
            print(f"🔴 Flutterwave API exception: {e}")
            return {
                "success": False,
                "message": f"Payment initialization failed: {str(e)}"
            }
    
    def verify_payment(self, transaction_id: str) -> Dict:
        """
        Verify a payment transaction
        
        Args:
            transaction_id: Flutterwave transaction ID
        
        Returns:
            Dict with verification status and details
        """
        
        url = f"{self.base_url}/transactions/{transaction_id}/verify"
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                transaction_data = data["data"]
                
                return {
                    "success": True,
                    "verified": transaction_data.get("status") == "successful",
                    "amount": transaction_data.get("amount"),
                    "currency": transaction_data.get("currency"),
                    "tx_ref": transaction_data.get("tx_ref"),
                    "transaction_id": transaction_data.get("id"),
                    "customer_email": transaction_data.get("customer", {}).get("email"),
                    "payment_type": transaction_data.get("payment_type"),
                    "charged_amount": transaction_data.get("charged_amount"),
                    "message": "Payment verified successfully"
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "message": data.get("message", "Verification failed")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "verified": False,
                "message": f"Verification failed: {str(e)}"
            }
    
    def verify_payment_by_reference(self, tx_ref: str) -> Dict:
        """
        Verify a payment using transaction reference
        
        Args:
            tx_ref: Transaction reference
        
        Returns:
            Dict with verification status and details
        """
        
        url = f"{self.base_url}/transactions/verify_by_reference"
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        params = {"tx_ref": tx_ref}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                transaction_data = data["data"]
                
                return {
                    "success": True,
                    "verified": transaction_data.get("status") == "successful",
                    "amount": transaction_data.get("amount"),
                    "currency": transaction_data.get("currency"),
                    "tx_ref": transaction_data.get("tx_ref"),
                    "transaction_id": transaction_data.get("id"),
                    "customer_email": transaction_data.get("customer", {}).get("email"),
                    "payment_type": transaction_data.get("payment_type"),
                    "charged_amount": transaction_data.get("charged_amount"),
                    "message": "Payment verified successfully"
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "message": data.get("message", "Verification failed")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "verified": False,
                "message": f"Verification failed: {str(e)}"
            }
    
    def get_transaction_fee(self, amount: float, currency: str = "NGN") -> float:
        """
        Calculate Flutterwave transaction fee
        
        Args:
            amount: Transaction amount
            currency: Currency code
        
        Returns:
            Transaction fee amount
        """
        # Flutterwave Nigeria charges 1.4% capped at NGN 2,000
        if currency == "NGN":
            fee = amount * 0.014
            return min(fee, 2000)
        else:
            # For other currencies, 3.8%
            return amount * 0.038
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict:
        """
        Refund a payment
        
        Args:
            transaction_id: Flutterwave transaction ID
            amount: Amount to refund (optional, defaults to full amount)
        
        Returns:
            Dict with refund status
        """
        
        url = f"{self.base_url}/transactions/{transaction_id}/refund"
        
        payload = {}
        if amount:
            payload["amount"] = amount
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "message": "Refund processed successfully",
                    "refund_id": data["data"].get("id")
                }
            else:
                return {
                    "success": False,
                    "message": data.get("message", "Refund failed")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Refund failed: {str(e)}"
            }

# Singleton instance
flutterwave_service = FlutterwaveService()
