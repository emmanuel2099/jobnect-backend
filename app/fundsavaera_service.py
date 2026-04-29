"""
Fundsavaera Payment Integration Service
"""
import requests
import os
import hashlib
import json
from typing import Optional, Dict
from datetime import datetime

class FundsavaeraService:
    """Service for handling Fundsavaera payments"""
    
    def __init__(self):
        self.pub_key = os.getenv("FV_PUB_KEY", "")
        self.sec_key = os.getenv("FV_SEC_KEY", "")
        self.base_url = "https://api.fundsavaera.co/v1"
    
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
        Initialize a payment with Fundsavaera
        
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
        
        print(f"🔵 Initializing Fundsavaera payment:")
        print(f"  - Amount: {amount}")
        print(f"  - Email: {email}")
        print(f"  - Phone: {phone}")
        print(f"  - Name: {name}")
        print(f"  - TX Ref: {tx_ref}")
        print(f"  - Pub Key: {self.pub_key[:20]}...")
        print(f"  - Sec Key: {self.sec_key[:20]}...")
        print(f"  - Base URL: {self.base_url}")
        
        url = f"{self.base_url}/payment/initialize"
        
        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": currency,
            "redirect_url": redirect_url or "https://your-app.com/payment/callback",
            "customer": {
                "email": email,
                "name": name,
                "phone": phone
            },
            "customizations": {
                "title": "Eagle's Pride Payment",
                "description": f"Payment for Eagle's Pride services - {tx_ref}"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.pub_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"🔵 Making request to: {url}")
            print(f"🔵 Payload: {json.dumps(payload, indent=2)}")
            print(f"🔵 Headers: {headers}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"🔵 Response Status: {response.status_code}")
            print(f"🔵 Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔵 Parsed Response: {json.dumps(data, indent=2)}")
                
                if data.get("status") == "success":
                    payment_link = data.get("data", {}).get("payment_url")
                    print(f"🔵 Payment Link: {payment_link}")
                    
                    return {
                        "success": True,
                        "payment_link": payment_link,
                        "tx_ref": tx_ref,
                        "access_code": data.get("data", {}).get("access_code")
                    }
                else:
                    error_msg = data.get("message", "Payment initialization failed")
                    print(f"🔵 Payment Failed: {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg
                    }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"🔵 HTTP Error: {error_msg}")
                return {
                    "success": False,
                    "message": error_msg
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Payment initialization timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Connection error - please check internet"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Payment initialization error: {str(e)}"
            }
    
    def verify_payment(
        self,
        tx_ref: str
    ) -> Dict:
        """
        Verify a payment with Fundsavaera
        
        Args:
            tx_ref: Transaction reference to verify
        
        Returns:
            Dict with verification status
        """
        
        url = f"{self.base_url}/payment/verify/{tx_ref}"
        
        headers = {
            "Authorization": f"Bearer {self.sec_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    payment_data = data.get("data", {})
                    return {
                        "success": True,
                        "status": payment_data.get("status"),
                        "amount": payment_data.get("amount"),
                        "currency": payment_data.get("currency"),
                        "tx_ref": payment_data.get("tx_ref"),
                        "flw_ref": payment_data.get("flw_ref"),
                        "customer": payment_data.get("customer"),
                        "paid_at": payment_data.get("paid_at")
                    }
                else:
                    return {
                        "success": False,
                        "message": data.get("message", "Payment verification failed")
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Payment verification timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Connection error - please check internet"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Payment verification error: {str(e)}"
            }
    
    def generate_transaction_ref(self) -> str:
        """Generate unique transaction reference"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(hashlib.md5(f"{timestamp}{email}".encode()).hexdigest())[:8]
        return f"FV_{timestamp}_{random_suffix}"
