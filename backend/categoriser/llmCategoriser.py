from typing import Callable, Optional, List
from categoriser.companyOverrides import getCompanyOverride

TARGET_CATEGORIES: List[str] = [
    "travel",
    "transport",
    "dining",
    "shopping",
    "insurance",
    "utilities",
    "misc",  # For person names and non-business transactions
    "ignore",  # For bank transactions like interest, fees, transfers
]


class LlmCategoriser:
    """
    LLM-based categoriser for transaction merchants / company_person fields.

    You pass in a `predict_fn` that knows how to call Phi-3 Mini (or any
    other model). The function should accept a single string prompt and
    return the model's raw text response.
    """

    def __init__(self, predict_fn: Callable[[str], str]):
        self.predict_fn = predict_fn

    def build_prompt(
        self,
        company_person: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Build a classification prompt for the LLM based on the merchant/company name
        and optional extra description.
        """
        print("=== DEBUG PROMPT INPUT ===")
        print(company_person, description)
        print("=== END DEBUG ===")
        details = f'Company/person: "{company_person}"'
        if description:
            details += f'\nAdditional details: "{description}"'

        instruction = (
            "You are classifying credit card transactions into exactly one category: "
            f"{', '.join(TARGET_CATEGORIES)}.\n\n"
            "Guidelines:\n"
            "- 'dining': cafes, restaurants, food stalls, juice shops, salad bars, drink stalls.\n"
            "- 'shopping': retail shops, supermarkets, groceries, fashion, electronics, malls.\n"
            "- 'transport': taxis, ride-hailing (e.g. grab), buses, trains, fuel, parking, tolls.\n"
            "- 'travel': hotels, airlines, travel agencies, tours, overseas stays.\n"
            "- 'insurance': insurance companies, premiums, protection plans.\n"
            "- 'utilities': electricity, water, gas, mobile, internet, telco bills.\n"
            "- 'ignore': bank fees, interest, charges, ATM withdrawals, bank transfers.\n"
            "- 'misc': ONLY if it is clearly a person's name or there is no reasonable business guess.\n\n"
            "Important:\n"
            "- The ONLY valid category words you may output are: "
            "travel, transport, dining, shopping, insurance, utilities, misc, ignore.\n"
            "If you think 'groceries' is correct, you MUST output 'shopping'.\n"
            "Very important:\n"
            "- If the name looks like a shop, restaurant, drink stall, grocery, or brand, "
            "choose the closest business category (usually 'dining' or 'shopping'), "
            "NOT 'others'.\n\n"
            "Examples:\n"
            "- Merchant: 'JUICYFRESH' -> Category: dining\n"
            "- Merchant: 'WHOLLY GREENS' -> Category: shopping\n"
            "- Merchant: 'DRINKS STAL' -> Category: dining\n"
            "- Merchant: 'COCA' -> Category: dining\n"
            "- Merchant: 'GRAB' -> Category: transport\n"
            "- Merchant: 'M1 MAXX' -> Category: utilities\n"
            "- Merchant: 'ST LOGISTICS' -> Category: shopping\n"
            "- Merchant: 'NUR HAZAH' (looks like a person) -> Category: misc\n\n"
            "Now classify the merchant below. First think briefly about the best category, "
            "then on the last line output ONLY the category name in lowercase."
            "Do not write the word 'misc' anywhere unless you choose it as the final category.\n"

        )

        return instruction + "\\n\\n" + details

    def parse_category(self, raw_response: str) -> str:
        """
        Extract one of the target categories from the LLM's raw response.
        Prefer non-'others' categories if present.
        """
        text = raw_response.strip().lower()

        # If any <think>...</think> pattern exists, drop it
        if "</think>" in text:
            text = text.split("</think>", 1)[1].strip()

        # Take last non-empty line
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if lines:
            last = lines[-1].strip(" .,:;\"'")
            # If last is a clear category and not 'others', trust it
            if last in TARGET_CATEGORIES and last != "misc":
                return last

        # Otherwise, search for any non-'others' category in the text first
        for category in [c for c in TARGET_CATEGORIES if c != "misc"]:
            if category in text:
                return category
            

        # Only fall back to 'others' if nothing else found
        return "misc"

    def categorise(
        self,
        company_person: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Categorise a single transaction based on the company_person field and
        optional extra description.

        Checks company overrides first before using LLM.
        """
        # Check if there's a manual override for this company
        override = getCompanyOverride(company_person)
        if override:
            print(f"Using override for '{company_person}': {override}")
            return override

        # Otherwise, use LLM to categorize
        prompt = self.build_prompt(company_person, description)
        raw = self.predict_fn(prompt)

        # TEMP: debug output
        print("=== DEBUG LLM RAW RESPONSE ===")
        print(f"Merchant: {company_person!r}")
        print(repr(raw))
        print("=== END DEBUG ===")

        return self.parse_category(raw)
