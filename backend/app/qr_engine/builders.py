"""
QRMaster Pro — QR Data Builders (Strategy Pattern).

Each builder class knows how to format raw input into a QR-encodable string
for a specific QR type. The registry maps type keys to builder instances.
"""
from __future__ import annotations

import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


# --------------------------------------------------------------------------- #
#  Base builder
# --------------------------------------------------------------------------- #
class QRBuilderBase(ABC):
    """Abstract base for all QR data builders."""

    qr_type: str = "custom"
    label: str = "Custom"

    @abstractmethod
    def build(self, data: Dict[str, Any]) -> str:
        """Convert structured input into a QR-encodable string."""
        raise NotImplementedError

    def _req(self, data: Dict[str, Any], key: str) -> str:
        """Extract a required field or raise ValueError."""
        val = data.get(key)
        if val is None or str(val).strip() == "":
            raise ValueError(f"Field '{key}' is required for QR type '{self.qr_type}'")
        return str(val).strip()


# --------------------------------------------------------------------------- #
#  Simple text / URL
# --------------------------------------------------------------------------- #
class TextBuilder(QRBuilderBase):
    qr_type = "text"
    label = "Plain Text"

    def build(self, data: Dict[str, Any]) -> str:
        return self._req(data, "text")


class URLBuilder(QRBuilderBase):
    qr_type = "url"
    label = "Website URL"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url


# --------------------------------------------------------------------------- #
#  Communication
# --------------------------------------------------------------------------- #
class EmailBuilder(QRBuilderBase):
    qr_type = "email"
    label = "Email"

    def build(self, data: Dict[str, Any]) -> str:
        to = self._req(data, "email")
        subject = data.get("subject", "")
        body = data.get("body", "")
        params = urllib.parse.urlencode({"subject": subject, "body": body})
        return f"mailto:{to}?{params}"


class PhoneBuilder(QRBuilderBase):
    qr_type = "phone"
    label = "Phone Number"

    def build(self, data: Dict[str, Any]) -> str:
        return f"tel:{self._req(data, 'phone')}"


class SMSBuilder(QRBuilderBase):
    qr_type = "sms"
    label = "SMS"

    def build(self, data: Dict[str, Any]) -> str:
        number = self._req(data, "phone")
        message = data.get("message", "")
        return f"SMSTO:{number}:{message}"


class WhatsAppBuilder(QRBuilderBase):
    qr_type = "whatsapp"
    label = "WhatsApp Message"

    def build(self, data: Dict[str, Any]) -> str:
        number = self._req(data, "phone")
        number = number.replace("+", "").replace(" ", "")
        message = data.get("message", "")
        return f"https://wa.me/{number}?text={urllib.parse.quote(message)}"


class TelegramBuilder(QRBuilderBase):
    qr_type = "telegram"
    label = "Telegram"

    def build(self, data: Dict[str, Any]) -> str:
        username = self._req(data, "username")
        return f"https://t.me/{username.lstrip('@')}"


# --------------------------------------------------------------------------- #
#  Wi-Fi
# --------------------------------------------------------------------------- #
class WiFiBuilder(QRBuilderBase):
    qr_type = "wifi"
    label = "Wi-Fi Credentials"

    def build(self, data: Dict[str, Any]) -> str:
        ssid = self._req(data, "ssid")
        password = data.get("password", "")
        security = data.get("security", "WPA").upper()
        hidden = "true" if data.get("hidden", False) else "false"
        # Escape special chars
        ssid = ssid.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace(":", "\\:")
        password = password.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace(":", "\\:")
        return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden};;"


# --------------------------------------------------------------------------- #
#  vCard
# --------------------------------------------------------------------------- #
class VCardBuilder(QRBuilderBase):
    qr_type = "vcard"
    label = "vCard (Business Card)"

    def build(self, data: Dict[str, Any]) -> str:
        first = data.get("first_name", "")
        last = data.get("last_name", "")
        org = data.get("organization", "")
        title = data.get("title", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        url = data.get("url", "")
        address = data.get("address", "")

        lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{last};{first};;;", f"FN:{first} {last}".strip()]
        if org:
            lines.append(f"ORG:{org}")
        if title:
            lines.append(f"TITLE:{title}")
        if phone:
            lines.append(f"TEL;TYPE=CELL:{phone}")
        if email:
            lines.append(f"EMAIL:{email}")
        if url:
            lines.append(f"URL:{url}")
        if address:
            lines.append(f"ADR:;;{address};;;;")
        lines.append("END:VCARD")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Location
# --------------------------------------------------------------------------- #
class GeoBuilder(QRBuilderBase):
    qr_type = "geo"
    label = "GPS Coordinates"

    def build(self, data: Dict[str, Any]) -> str:
        lat = self._req(data, "latitude")
        lng = self._req(data, "longitude")
        return f"geo:{lat},{lng}"


class GoogleMapsBuilder(QRBuilderBase):
    qr_type = "google_maps"
    label = "Google Maps Location"

    def build(self, data: Dict[str, Any]) -> str:
        query = data.get("query", "")
        lat = data.get("latitude")
        lng = data.get("longitude")
        if lat and lng:
            return f"https://www.google.com/maps?q={lat},{lng}"
        if query:
            return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
        raise ValueError("Either 'query' or 'latitude'+'longitude' is required for google_maps")


# --------------------------------------------------------------------------- #
#  Social Media
# --------------------------------------------------------------------------- #
class _SocialURLBuilder(QRBuilderBase):
    """Generic builder for social profile URLs."""
    base_url: str = ""
    path_prefix: str = ""

    def build(self, data: Dict[str, Any]) -> str:
        username = self._req(data, "username").lstrip("@")
        return f"{self.base_url}{self.path_prefix}{username}"


class FacebookBuilder(_SocialURLBuilder):
    qr_type = "facebook"
    label = "Facebook"
    base_url = "https://facebook.com/"
    path_prefix = ""


class InstagramBuilder(_SocialURLBuilder):
    qr_type = "instagram"
    label = "Instagram"
    base_url = "https://instagram.com/"
    path_prefix = ""


class LinkedInBuilder(QRBuilderBase):
    qr_type = "linkedin"
    label = "LinkedIn"

    def build(self, data: Dict[str, Any]) -> str:
        username = self._req(data, "username")
        if username.startswith("http"):
            return username
        return f"https://linkedin.com/in/{username.lstrip('/')}"


class GitHubBuilder(_SocialURLBuilder):
    qr_type = "github"
    label = "GitHub"
    base_url = "https://github.com/"
    path_prefix = ""


class YouTubeBuilder(QRBuilderBase):
    qr_type = "youtube"
    label = "YouTube"

    def build(self, data: Dict[str, Any]) -> str:
        channel = self._req(data, "channel")
        if channel.startswith("http"):
            return channel
        if channel.startswith("@"):
            return f"https://youtube.com/{channel}"
        return f"https://youtube.com/@{channel}"


class TwitterBuilder(QRBuilderBase):
    qr_type = "twitter"
    label = "X (Twitter)"

    def build(self, data: Dict[str, Any]) -> str:
        username = self._req(data, "username").lstrip("@")
        return f"https://x.com/{username}"


# --------------------------------------------------------------------------- #
#  Payments
# --------------------------------------------------------------------------- #
class UPIBuilder(QRBuilderBase):
    qr_type = "upi"
    label = "UPI Payment"

    def build(self, data: Dict[str, Any]) -> str:
        vpa = self._req(data, "vpa")
        name = data.get("payee_name", "")
        amount = data.get("amount", "")
        note = data.get("note", "")
        params = []
        if name:
            params.append(f"pn={urllib.parse.quote(name)}")
        if amount:
            params.append(f"am={amount}")
        if note:
            params.append(f"tn={urllib.parse.quote(note)}")
        query = "&".join(params)
        return f"upi://pay?pa={vpa}&{query}" if query else f"upi://pay?pa={vpa}"


class GooglePayBuilder(UPIBuilder):
    qr_type = "google_pay"
    label = "Google Pay"


class PhonePeBuilder(UPIBuilder):
    qr_type = "phonepe"
    label = "PhonePe"


class PaytmBuilder(UPIBuilder):
    qr_type = "paytm"
    label = "Paytm"


# --------------------------------------------------------------------------- #
#  Crypto
# --------------------------------------------------------------------------- #
class BitcoinBuilder(QRBuilderBase):
    qr_type = "bitcoin"
    label = "Bitcoin Wallet"

    def build(self, data: Dict[str, Any]) -> str:
        address = self._req(data, "address")
        amount = data.get("amount", "")
        label = data.get("label", "")
        params = []
        if amount:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={urllib.parse.quote(label)}")
        query = "&".join(params)
        return f"bitcoin:{address}?{query}" if query else f"bitcoin:{address}"


class EthereumBuilder(QRBuilderBase):
    qr_type = "ethereum"
    label = "Ethereum Wallet"

    def build(self, data: Dict[str, Any]) -> str:
        address = self._req(data, "address")
        amount = data.get("amount", "")
        if amount:
            return f"ethereum:{address}?value={amount}"
        return f"ethereum:{address}"


# --------------------------------------------------------------------------- #
#  Events
# --------------------------------------------------------------------------- #
class EventBuilder(QRBuilderBase):
    qr_type = "event"
    label = "Event Details"

    def build(self, data: Dict[str, Any]) -> str:
        title = self._req(data, "title")
        location = data.get("location", "")
        start = data.get("start_datetime", "")
        end = data.get("end_datetime", "")
        description = data.get("description", "")
        lines = ["BEGIN:VEVENT", f"SUMMARY:{title}"]
        if location:
            lines.append(f"LOCATION:{location}")
        if start:
            lines.append(f"DTSTART:{start}")
        if end:
            lines.append(f"DTEND:{end}")
        if description:
            lines.append(f"DESCRIPTION:{description}")
        lines.append("END:VEVENT")
        return "\n".join(lines)


class CalendarEventBuilder(EventBuilder):
    qr_type = "calendar"
    label = "Calendar Event"


class MeetingLinkBuilder(QRBuilderBase):
    qr_type = "meeting"
    label = "Meeting Link"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith("http"):
            url = "https://" + url
        return url


class ZoomBuilder(QRBuilderBase):
    qr_type = "zoom"
    label = "Zoom"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith("http"):
            url = "https://" + url
        return url


class GoogleMeetBuilder(QRBuilderBase):
    qr_type = "google_meet"
    label = "Google Meet"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith("http"):
            url = "https://" + url
        return url


# --------------------------------------------------------------------------- #
#  App / Files
# --------------------------------------------------------------------------- #
class AppDownloadBuilder(QRBuilderBase):
    qr_type = "app_download"
    label = "App Download Link"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith("http"):
            url = "https://" + url
        return url


class FileLinkBuilder(QRBuilderBase):
    qr_type = "file_link"
    label = "File Link"

    def build(self, data: Dict[str, Any]) -> str:
        url = self._req(data, "url")
        if not url.startswith("http"):
            url = "https://" + url
        return url


class CustomBuilder(QRBuilderBase):
    qr_type = "custom"
    label = "Custom QR Data"

    def build(self, data: Dict[str, Any]) -> str:
        return self._req(data, "data")


# --------------------------------------------------------------------------- #
#  Registry
# --------------------------------------------------------------------------- #
class QRBuilderRegistry:
    """Maps QR type keys to builder instances."""

    def __init__(self) -> None:
        self._builders: Dict[str, QRBuilderBase] = {}
        self._labels: Dict[str, str] = {}

    def register(self, builder: QRBuilderBase) -> QRBuilderBase:
        self._builders[builder.qr_type] = builder
        self._labels[builder.qr_type] = builder.label
        return builder

    def get(self, qr_type: str) -> QRBuilderBase:
        if qr_type not in self._builders:
            raise ValueError(f"Unsupported QR type: '{qr_type}'")
        return self._builders[qr_type]

    def build(self, qr_type: str, data: Dict[str, Any]) -> str:
        return self.get(qr_type).build(data)

    def all_types(self) -> Dict[str, str]:
        return dict(self._labels)

    def is_supported(self, qr_type: str) -> bool:
        return qr_type in self._builders


# Singleton registry — register all builders
registry = QRBuilderRegistry()
for _builder_cls in [
    TextBuilder, URLBuilder, EmailBuilder, PhoneBuilder, SMSBuilder,
    WhatsAppBuilder, TelegramBuilder, WiFiBuilder, VCardBuilder,
    GeoBuilder, GoogleMapsBuilder, FacebookBuilder, InstagramBuilder,
    LinkedInBuilder, GitHubBuilder, YouTubeBuilder, TwitterBuilder,
    UPIBuilder, GooglePayBuilder, PhonePeBuilder, PaytmBuilder,
    BitcoinBuilder, EthereumBuilder, EventBuilder, CalendarEventBuilder,
    MeetingLinkBuilder, ZoomBuilder, GoogleMeetBuilder,
    AppDownloadBuilder, FileLinkBuilder, CustomBuilder,
]:
    registry.register(_builder_cls())


__all__ = [
    "QRBuilderBase",
    "QRBuilderRegistry",
    "registry",
    # All builders
    "TextBuilder", "URLBuilder", "EmailBuilder", "PhoneBuilder", "SMSBuilder",
    "WhatsAppBuilder", "TelegramBuilder", "WiFiBuilder", "VCardBuilder",
    "GeoBuilder", "GoogleMapsBuilder", "FacebookBuilder", "InstagramBuilder",
    "LinkedInBuilder", "GitHubBuilder", "YouTubeBuilder", "TwitterBuilder",
    "UPIBuilder", "GooglePayBuilder", "PhonePeBuilder", "PaytmBuilder",
    "BitcoinBuilder", "EthereumBuilder", "EventBuilder", "CalendarEventBuilder",
    "MeetingLinkBuilder", "ZoomBuilder", "GoogleMeetBuilder",
    "AppDownloadBuilder", "FileLinkBuilder", "CustomBuilder",
]