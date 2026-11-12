"""Ported from api/Models/Localization/ServiceTiers.cs."""

from __future__ import annotations


class ServiceTiers:
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

    @staticmethod
    def members_for(tier: str) -> int:
        if tier == ServiceTiers.SILVER:
            return 3
        if tier == ServiceTiers.GOLD:
            return 6
        if tier == ServiceTiers.PLATINUM:
            return 10
        # The detail embeds .NET's ArgumentException Message suffix verbatim
        # (" (Parameter 'tier')") so error bodies match.
        raise ValueError(f"Unknown service tier '{tier}'. (Parameter 'tier')")
