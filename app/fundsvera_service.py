"""
FundsVera Payment Integration Service
"""
import os
from typing import Dict, Optional

import requests


class FundsVeraService:
    """Service for handling FundsVera payments."""

    def __init__(self):
        self.public_key = os.getenv("FUNDSVERA_PUBLIC_KEY", "").strip()
        self.secret_key = os.getenv("FUNDSVERA_SECRET_KEY", "").strip()
        self.base_url = os.getenv("FUNDSVERA_BASE_URL", "https://fundsvera.co/api/v1").strip().rstrip("/")
        self.timeout_seconds = 30

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "x-api-key": self.secret_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def initialize_payment(
        self,
        amount: float,
        email: str,
        phone: str,
        name: str,
        tx_ref: str,
        redirect_url: str = "",
        currency: str = "NGN",
    ) -> Dict:
        """
        Initialize a payment session with FundsVera.
        """
        payload = {
            "reference": tx_ref,
            "amount": float(amount),
            "currency": currency,
            "email": email,
            "phone": phone,
            "name": name,
            "callback_url": redirect_url or "",
            "metadata": {
                "source": "jobnect-backend",
            },
        }

        candidate_endpoints = [
            f"{self.base_url}/payments/initialize",
            f"{self.base_url}/payment/initialize",
            f"{self.base_url}/transactions/initialize",
        ]

        last_error = "Unable to initialize payment"
        for url in candidate_endpoints:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()

                success = bool(data.get("success", False) or data.get("status") in {"success", "ok"})
                if not success:
                    last_error = data.get("message") or data.get("error") or last_error
                    continue

                payment_link = (
                    data.get("data", {}).get("payment_link")
                    or data.get("data", {}).get("checkout_url")
                    or data.get("data", {}).get("link")
                    or data.get("payment_link")
                    or data.get("checkout_url")
                    or data.get("link")
                )

                return {
                    "success": True,
                    "payment_link": payment_link,
                    "tx_ref": tx_ref,
                    "message": data.get("message", "Payment initialized successfully"),
                    "raw": data,
                }
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
            except ValueError:
                last_error = "FundsVera returned invalid JSON"

        return {
            "success": False,
            "message": f"FundsVera initialization failed: {last_error}",
        }

    def verify_payment_by_reference(self, tx_ref: str) -> Dict:
        """
        Verify payment using transaction reference.
        """
        candidate_requests = [
            ("GET", f"{self.base_url}/payments/verify/{tx_ref}", None),
            ("GET", f"{self.base_url}/payment/verify/{tx_ref}", None),
            ("GET", f"{self.base_url}/transactions/verify/{tx_ref}", None),
            ("POST", f"{self.base_url}/payments/verify", {"reference": tx_ref}),
            ("POST", f"{self.base_url}/payment/verify", {"reference": tx_ref}),
        ]

        last_error = "Unable to verify payment"
        for method, url, body in candidate_requests:
            try:
                if method == "GET":
                    response = requests.get(url, headers=self._headers(), timeout=self.timeout_seconds)
                else:
                    response = requests.post(
                        url, json=body, headers=self._headers(), timeout=self.timeout_seconds
                    )
                response.raise_for_status()
                data = response.json()

                success = bool(data.get("success", False) or data.get("status") in {"success", "ok"})
                payment_data = data.get("data", {})
                verified = (
                    payment_data.get("status") in {"successful", "success", "paid", "completed"}
                    or data.get("payment_status") in {"successful", "success", "paid", "completed"}
                )

                if not success and not verified:
                    last_error = data.get("message") or data.get("error") or last_error
                    continue

                return {
                    "success": True,
                    "verified": bool(verified),
                    "amount": payment_data.get("amount") or data.get("amount"),
                    "currency": payment_data.get("currency") or data.get("currency"),
                    "tx_ref": payment_data.get("reference")
                    or payment_data.get("tx_ref")
                    or tx_ref,
                    "transaction_id": payment_data.get("id") or data.get("transaction_id"),
                    "customer_email": payment_data.get("email")
                    or payment_data.get("customer", {}).get("email"),
                    "payment_type": payment_data.get("payment_method") or payment_data.get("channel"),
                    "charged_amount": payment_data.get("charged_amount") or payment_data.get("amount"),
                    "message": data.get("message", "Payment verified"),
                    "raw": data,
                }
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
            except ValueError:
                last_error = "FundsVera returned invalid JSON"

        return {
            "success": False,
            "verified": False,
            "message": f"FundsVera verification failed: {last_error}",
        }

    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict:
        """
        Refund a payment.
        """
        payload: Dict[str, object] = {"transaction_id": transaction_id}
        if amount is not None:
            payload["amount"] = float(amount)

        candidate_endpoints = [
            f"{self.base_url}/payments/refund",
            f"{self.base_url}/payment/refund",
            f"{self.base_url}/transactions/refund",
        ]

        last_error = "Unable to process refund"
        for url in candidate_endpoints:
            try:
                response = requests.post(
                    url, json=payload, headers=self._headers(), timeout=self.timeout_seconds
                )
                response.raise_for_status()
                data = response.json()
                success = bool(data.get("success", False) or data.get("status") in {"success", "ok"})

                if success:
                    return {
                        "success": True,
                        "message": data.get("message", "Refund processed successfully"),
                        "refund_id": data.get("data", {}).get("id") or data.get("refund_id"),
                    }
                last_error = data.get("message") or data.get("error") or last_error
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
            except ValueError:
                last_error = "FundsVera returned invalid JSON"

        return {
            "success": False,
            "message": f"FundsVera refund failed: {last_error}",
        }


fundsvera_service = FundsVeraService()
