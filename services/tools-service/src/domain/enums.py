"""Domain enumerations.

Only the columns the frozen schema constrains with an explicit value set are modelled
as enums (leaves.type, assets.type, jira_tickets.type). Free-text columns (status,
priority, region, segment, ...) stay plain strings on the entities.
"""
from enum import Enum


class LeaveType(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"


class AssetType(str, Enum):
    LAPTOP = "laptop"
    VPN = "vpn"
    PHONE = "phone"


class TicketType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    EPIC = "epic"


class DocumentTemplate(str, Enum):
    """Templates supported by doc_generate (T9)."""

    OFFER_LETTER = "offer_letter"
    RESIGNATION = "resignation"
    MEETING_MINUTES = "meeting_minutes"
    SOP = "sop"
