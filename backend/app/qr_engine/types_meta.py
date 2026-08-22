"""
QRMaster Pro — QR Type Metadata.

Describes the input fields required for each QR type. Used by the frontend
to render dynamic forms and by the API to document supported types.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _field(name: str, label: str, ftype: str = "text", required: bool = True,
           placeholder: str = "", options: List[str] = None, default: Any = None) -> Dict[str, Any]:
    f: Dict[str, Any] = {"name": name, "label": label, "type": ftype, "required": required,
                         "placeholder": placeholder}
    if options:
        f["options"] = options
    if default is not None:
        f["default"] = default
    return f


QR_TYPES_META: Dict[str, Dict[str, Any]] = {
    "text": {
        "key": "text", "label": "Plain Text", "icon": "BsType", "category": "general",
        "fields": [_field("text", "Text", "textarea", True, "Enter any text...")],
    },
    "url": {
        "key": "url", "label": "Website URL", "icon": "BsLink45", "category": "general",
        "fields": [_field("url", "URL", "text", True, "https://example.com")],
    },
    "email": {
        "key": "email", "label": "Email", "icon": "BsEnvelope", "category": "communication",
        "fields": [
            _field("email", "Email Address", "email", True, "name@example.com"),
            _field("subject", "Subject", "text", False, "Hello"),
            _field("body", "Message", "textarea", False, "Your message..."),
        ],
    },
    "phone": {
        "key": "phone", "label": "Phone Number", "icon": "BsTelephone", "category": "communication",
        "fields": [_field("phone", "Phone Number", "tel", True, "+1234567890")],
    },
    "sms": {
        "key": "sms", "label": "SMS", "icon": "BsChatText", "category": "communication",
        "fields": [
            _field("phone", "Phone Number", "tel", True, "+1234567890"),
            _field("message", "Message", "textarea", False, "Hello!"),
        ],
    },
    "whatsapp": {
        "key": "whatsapp", "label": "WhatsApp", "icon": "BsWhatsapp", "category": "communication",
        "fields": [
            _field("phone", "Phone Number", "tel", True, "+1234567890"),
            _field("message", "Message", "textarea", False, "Hello!"),
        ],
    },
    "telegram": {
        "key": "telegram", "label": "Telegram", "icon": "BsTelegram", "category": "social",
        "fields": [_field("username", "Username", "text", True, "@username")],
    },
    "wifi": {
        "key": "wifi", "label": "Wi-Fi", "icon": "BsWifi", "category": "general",
        "fields": [
            _field("ssid", "Network Name (SSID)", "text", True, "MyWiFi"),
            _field("password", "Password", "text", False, "password"),
            _field("security", "Security", "select", True, "", ["WPA", "WEP", "nopass"], "WPA"),
            _field("hidden", "Hidden Network", "checkbox", False, "", None, False),
        ],
    },
    "vcard": {
        "key": "vcard", "label": "vCard", "icon": "BsPersonVcard", "category": "business",
        "fields": [
            _field("first_name", "First Name", "text", True, "John"),
            _field("last_name", "Last Name", "text", False, "Doe"),
            _field("organization", "Organization", "text", False, "Company Inc."),
            _field("title", "Job Title", "text", False, "Engineer"),
            _field("phone", "Phone", "tel", False, "+1234567890"),
            _field("email", "Email", "email", False, "john@example.com"),
            _field("url", "Website", "text", False, "https://example.com"),
            _field("address", "Address", "textarea", False, "123 Main St"),
        ],
    },
    "geo": {
        "key": "geo", "label": "GPS Coordinates", "icon": "BsGeoAlt", "category": "location",
        "fields": [
            _field("latitude", "Latitude", "number", True, "12.9716"),
            _field("longitude", "Longitude", "number", True, "77.5946"),
        ],
    },
    "google_maps": {
        "key": "google_maps", "label": "Google Maps", "icon": "BsMap", "category": "location",
        "fields": [
            _field("query", "Location Search", "text", False, "Eiffel Tower, Paris"),
            _field("latitude", "Latitude (optional)", "number", False, ""),
            _field("longitude", "Longitude (optional)", "number", False, ""),
        ],
    },
    "facebook": {
        "key": "facebook", "label": "Facebook", "icon": "BsFacebook", "category": "social",
        "fields": [_field("username", "Username / Page", "text", True, "my.page")],
    },
    "instagram": {
        "key": "instagram", "label": "Instagram", "icon": "BsInstagram", "category": "social",
        "fields": [_field("username", "Username", "text", True, "@username")],
    },
    "linkedin": {
        "key": "linkedin", "label": "LinkedIn", "icon": "BsLinkedin", "category": "social",
        "fields": [_field("username", "Username / URL", "text", True, "username or full URL")],
    },
    "github": {
        "key": "github", "label": "GitHub", "icon": "BsGithub", "category": "social",
        "fields": [_field("username", "Username", "text", True, "username")],
    },
    "youtube": {
        "key": "youtube", "label": "YouTube", "icon": "BsYoutube", "category": "social",
        "fields": [_field("channel", "Channel / URL", "text", True, "@channel or full URL")],
    },
    "twitter": {
        "key": "twitter", "label": "X (Twitter)", "icon": "BsTwitterX", "category": "social",
        "fields": [_field("username", "Username", "text", True, "@username")],
    },
    "upi": {
        "key": "upi", "label": "UPI Payment", "icon": "BsCurrencyRupee", "category": "payments",
        "fields": [
            _field("vpa", "UPI VPA", "text", True, "name@bank"),
            _field("payee_name", "Payee Name", "text", False, "John Doe"),
            _field("amount", "Amount", "number", False, "100"),
            _field("note", "Note", "text", False, "Payment for..."),
        ],
    },
    "google_pay": {
        "key": "google_pay", "label": "Google Pay", "icon": "BsGoogle", "category": "payments",
        "fields": [
            _field("vpa", "UPI VPA", "text", True, "name@okhdfcbank"),
            _field("payee_name", "Payee Name", "text", False, "John Doe"),
            _field("amount", "Amount", "number", False, "100"),
        ],
    },
    "phonepe": {
        "key": "phonepe", "label": "PhonePe", "icon": "BsPhone", "category": "payments",
        "fields": [
            _field("vpa", "UPI VPA", "text", True, "name@ybl"),
            _field("payee_name", "Payee Name", "text", False, "John Doe"),
            _field("amount", "Amount", "number", False, "100"),
        ],
    },
    "paytm": {
        "key": "paytm", "label": "Paytm", "icon": "BsWallet", "category": "payments",
        "fields": [
            _field("vpa", "UPI VPA", "text", True, "name@paytm"),
            _field("payee_name", "Payee Name", "text", False, "John Doe"),
            _field("amount", "Amount", "number", False, "100"),
        ],
    },
    "bitcoin": {
        "key": "bitcoin", "label": "Bitcoin", "icon": "BsCurrencyBitcoin", "category": "payments",
        "fields": [
            _field("address", "Wallet Address", "text", True, "bc1q..."),
            _field("amount", "Amount (BTC)", "number", False, "0.001"),
            _field("label", "Label", "text", False, "Donation"),
        ],
    },
    "ethereum": {
        "key": "ethereum", "label": "Ethereum", "icon": "BsCurrencyExchange", "category": "payments",
        "fields": [
            _field("address", "Wallet Address", "text", True, "0x..."),
            _field("amount", "Amount (ETH)", "number", False, "0.01"),
        ],
    },
    "event": {
        "key": "event", "label": "Event", "icon": "BsCalendarEvent", "category": "events",
        "fields": [
            _field("title", "Event Title", "text", True, "Meeting"),
            _field("location", "Location", "text", False, "Office"),
            _field("start_datetime", "Start (YYYYMMDDTHHMMSS)", "text", False, "20260101T100000"),
            _field("end_datetime", "End (YYYYMMDDTHHMMSS)", "text", False, "20260101T110000"),
            _field("description", "Description", "textarea", False, ""),
        ],
    },
    "calendar": {
        "key": "calendar", "label": "Calendar Event", "icon": "BsCalendar2Event", "category": "events",
        "fields": [
            _field("title", "Title", "text", True, "Appointment"),
            _field("location", "Location", "text", False, ""),
            _field("start_datetime", "Start", "text", False, ""),
            _field("end_datetime", "End", "text", False, ""),
            _field("description", "Description", "textarea", False, ""),
        ],
    },
    "meeting": {
        "key": "meeting", "label": "Meeting Link", "icon": "BsCameraVideo", "category": "events",
        "fields": [_field("url", "Meeting URL", "text", True, "https://meet.example.com/abc")],
    },
    "zoom": {
        "key": "zoom", "label": "Zoom", "icon": "BsCameraVideo", "category": "events",
        "fields": [_field("url", "Zoom Meeting URL", "text", True, "https://zoom.us/j/123")],
    },
    "google_meet": {
        "key": "google_meet", "label": "Google Meet", "icon": "BsGoogle", "category": "events",
        "fields": [_field("url", "Meet URL", "text", True, "https://meet.google.com/abc-defg-hij")],
    },
    "app_download": {
        "key": "app_download", "label": "App Download", "icon": "BsDownload", "category": "files",
        "fields": [_field("url", "App Store / Download URL", "text", True, "https://...")],
    },
    "file_link": {
        "key": "file_link", "label": "File Link", "icon": "BsFileEarmark", "category": "files",
        "fields": [_field("url", "File URL (Drive/Dropbox/OneDrive)", "text", True, "https://...")],
    },
    "custom": {
        "key": "custom", "label": "Custom Data", "icon": "BsGear", "category": "general",
        "fields": [_field("data", "Custom Data", "textarea", True, "Any data to encode...")],
    },
}


def get_all_types() -> List[Dict[str, Any]]:
    """Return metadata for all QR types as a list."""
    return list(QR_TYPES_META.values())


def get_type_meta(qr_type: str) -> Dict[str, Any]:
    """Return metadata for a single QR type."""
    if qr_type not in QR_TYPES_META:
        raise ValueError(f"Unknown QR type: {qr_type}")
    return QR_TYPES_META[qr_type]