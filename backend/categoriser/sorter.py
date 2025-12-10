# transactions -> paynow (3/4 lines)
# transactions -> DR debit card/ NETS (3 lines)
# transactions -> CR salary/Inward Credit (4 lines)
# transactions -> Fund Transfer (3-4 lines)
# transactions -> bill payment (3 lines)

# keep going through the output until hit date xx containing terms like Paynow, DR, CR, Fund, Bill
import os
import json
from categoriser.categoryDictionary import FINANCE_TERMS
import operator as op
import re


class OcrSorter:
    def __init__(self):
        pass

    def findScript(self):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to backend, then access output.json
        transactions_output = os.path.join(
            script_dir, "..", "ocr/ocrOutPut/output.json"
        )

        print(f"Looking for file at: {os.path.abspath(transactions_output)}")
        with open(transactions_output, "r", encoding="utf-8") as f:
            transactions = json.load(f)
            print(f"Loaded {len(transactions)} transactions")
        return transactions

    def checkStartTransaction(self, transaction):

        text = transaction.get("raw_text", "").lower()

        for category, terms in FINANCE_TERMS.items():
            # Check if ANY of the terms in the list are in the transaction text using word boundaries
            for term in terms:
                # Use word boundary \b to match whole words only
                pattern = r"\b" + re.escape(term) + r"\b"
                if re.search(pattern, text):
                    return category
        return None

    def groupTransactions(self, transactions):
        counter = 0
        transactionList = []
        currentListIndex = 0
        print(len(transactions))
        while counter < len(transactions):
            category = self.checkStartTransaction(transactions[counter])
            if category:  # If a category is found, this is a start transaction
                print(
                    f"Start transaction found at index {counter} - Category: {category}"
                )
                # Create a new list for this transaction group
                transactionList.append(
                    {"category": category, "lines": [transactions[counter]]}
                )
                currentListIndex += 1
            else:
                if currentListIndex != 0:
                    # Append to the current transaction group
                    transactionList[currentListIndex - 1]["lines"].append(
                        transactions[counter]
                    )

            counter += 1
        return transactionList

    # Cleaning this transactionsList into this format:
    # [date, transaction type(paynow, cr, dr), amount ,company]
    # cleaning company/person name without any suffix like pte ltd

    def cleanTransactions(self, transactionList):
        cleanedTransactions = []
        for transaction in transactionList:
            lines = transaction["lines"]
            category = transaction["category"]

            # Skip interest transactions (not expenses - these are income/bank transactions)
            if category == "interest":
                print(f"Skipping interest transaction")
                continue

            # Extract date and amount from first line
            date = lines[0]["parts"][0]  # date
            amount = lines[0]["parts"][2]  # amount

            # Extract company/person from appropriate line based on category
            if category == "nets":
                companyPerson = lines[1]["parts"][0].upper()
            else:
                companyPerson = lines[2]["parts"][0].upper()

            cleanedCompanyPerson = self.cleanCompanyPerson(companyPerson)

            cleanedTransactions.append(
                {
                    "date": date,
                    "category": category,
                    "amount": amount,
                    "company_person": cleanedCompanyPerson,
                }
            )
        return cleanedTransactions

    def cleanCompanyPerson(self, raw: str) -> str:
        SUFFIX_STOP_WORDS = {
            "PTE",
            "LTD",
            "PTE.",
            "LTD.",
            "PTY",
            "CO",
            "CO.",
            "LLC",
            "CORP",
            "CORPORATION",
            "SINGAPORE",
            "SG",
        }

        s = raw.upper().strip()

        # Split on spaces and commas
        tokens = re.split(r"[,\s]+", s)
        cleanedParts = []

        for token in tokens:
            if not token:
                continue

            # Skip leading WWW
            if token == "WWW":
                continue

            # For domains, keep part before first dot
            if "." in token:
                token = token.split(".")[0]

            # Take only leading letters from tokens like STAL08543300
            # m = re.match(r"[A-Z]+", token)
            # if not m:
            #     continue
            # word = m.group(0)

            # Stop at company suffixes (PTE, LTD, etc.)
            if token in SUFFIX_STOP_WORDS:
                break
            
            cleanedParts.append(token)

        return " ".join(cleanedParts)
