"""
Company-specific category overrides.
Use this for companies where the name is misleading or keyword matching fails.
"""

# Companies that should override keyword-based categorization
COMPANY_OVERRIDES = {
    # Format: "COMPANY NAME": "category"
    # Shopping
    "ST LOGISTICS": "shopping",  # Army clothing supplier, not transport
    # Person names (common ones you see)
    "NUR ZANAH": "others",  # Person name
    # Transport
    "GRAB": "transport",
    "GRAB TRANSPORT": "transport",
    "COMFORT DELGRO": "transport",
    "GOJEK": "transport",
    # Dining
    "MCDONALD": "dining",
    "MCDONALDS": "dining",
    "KFC": "dining",
    "STARBUCKS": "dining",
    # Add more as you discover them
}


def getCompanyOverride(company_name: str) -> str | None:
    """
    Check if a company has a specific category override.

    Args:
        company_name: The cleaned company/merchant name

    Returns:
        Category string if override exists, None otherwise
    """
    # Normalize the company name for matching
    normalized = company_name.upper().strip()

    return COMPANY_OVERRIDES.get(normalized)
