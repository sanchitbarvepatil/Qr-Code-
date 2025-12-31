import os
import urllib.parse
from io import BytesIO
from typing import Dict

import streamlit as st
import qrcode
from PIL import Image


# ==============================
# CONFIG
# ==============================

APP_TITLE = "D-PAY Secure QR"
DEFAULT_UPI_ID = os.getenv("MERCHANT_UPI_ID", "8788072107@ybl")


# ==============================
# QR SERVICE
# ==============================

class QRService:
    """Generate secure, high-quality QR codes."""

    @staticmethod
    @st.cache_data(show_spinner=False)
    def create_qr(data: str) -> BytesIO:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="#0f172a",
            back_color="white"
        ).convert("RGB")

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer


# ==============================
# UTILITY
# ==============================

def build_upi_payload(
    upi_id: str,
    name: str,
    amount: float,
    currency: str,
    note: str
) -> str:
    if not upi_id or "@" not in upi_id:
        raise ValueError("Invalid UPI ID")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    params: Dict[str, str] = {
        "pa": upi_id.strip(),
        "pn": name.strip(),
        "am": f"{amount:.2f}",
        "cu": currency,
    }

    if note:
        params["tn"] = note.strip()

    return f"upi://pay?{urllib.parse.urlencode(params)}"


# ==============================
# UI STYLE
# ==============================

def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at center, #1e293b, #0f172a);
            color: #f8fafc;
        }

        .card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 2rem;
        }

        .stButton>button {
            width: 100%;
            border-radius: 14px;
            padding: 0.7rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border: none;
            color: white;
        }

        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 20px rgba(0,210,255,0.4);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================
# MAIN APP
# ==============================

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="💳",
        layout="centered",
    )

    inject_css()

    st.markdown(
        "<h1 style='text-align:center;'>D-PAY <span style='color:#00d2ff'>SECURE</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;opacity:0.7;'>UPI QR Payment Generator</p>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            merchant = st.text_input("Merchant Name", "D-PAY Store")
            amount = st.number_input("Amount (INR)", min_value=1.0, step=10.0)

        with col2:
            note = st.text_input("Payment Note (optional)")
            currency = st.selectbox("Currency", ["INR"], disabled=True)

        if st.button("Generate QR Code"):
            try:
                payload = build_upi_payload(
                    upi_id=DEFAULT_UPI_ID,
                    name=merchant,
                    amount=amount,
                    currency=currency,
                    note=note,
                )

                qr_img = QRService.create_qr(payload)

                st.divider()
                st.image(
                    qr_img,
                    caption="Scan with any UPI app (GPay / PhonePe / Paytm)",
                    use_container_width=True,
                )

                st.download_button(
                    "Download QR Code",
                    qr_img.getvalue(),
                    file_name="upi_qr.png",
                    mime="image/png",
                )

            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center;opacity:0.4;font-size:11px;margin-top:2rem;">
        Secure QR Generation • No data stored • Client-side only
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
