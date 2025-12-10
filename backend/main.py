from ocr.ocr import Ocr
from ocr.parser import OcrParser
from datetime import datetime
from pathlib import Path
import json
from categoriser.sorter import OcrSorter
from categoriser.llmService import LLMService
from categoriser.llmCategoriser import LlmCategoriser

ocr_engine = Ocr()
# Replace with a valid image path or ensure the path exists
result = ocr_engine.perform_ocr("bankStatements/AUG 2025_20251126153531065.pdf")
# print(result)
# ocr_engine.print_result(result)
parser = OcrParser()
transactions = parser.parse_transactions(result)

# Write to JSON file for easier data manipulation
output_dir = Path(__file__).parent / "ocr" / "ocrOutput"
output_dir.mkdir(parents=True, exist_ok=True)

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = output_dir / "output.json"

with output_path.open("w", encoding="utf-8") as f:
    json.dump(transactions, f, indent=2, ensure_ascii=False)

print(f"Results written to {output_path} ({len(transactions)} transactions)")

# Extract transactions
# Clean transaction company/person names

sorter = OcrSorter()
transactions = sorter.findScript()
# print(transactions)
groupedTransactions = sorter.groupTransactions(transactions)
print(groupedTransactions)
cleanedTransactions = sorter.cleanTransactions(groupedTransactions)

print("CLEANED TRANSACTIONS:")
print(json.dumps(cleanedTransactions, indent=2))

# Initialize Phi-3 model (this takes time on first run)
print("\n" + "=" * 60)
print("Initializing LLM for categorization...")
print("=" * 60)
llmModel = LLMService()

# Categorize transactions
llmCategoriser = LlmCategoriser(predict_fn=llmModel.predict)

print(f"\nCategorizing {len(cleanedTransactions)} transactions...")
for i, transaction in enumerate(cleanedTransactions, 1):
    print(
        f"[{i}/{len(cleanedTransactions)}] Categorizing: {transaction['company_person']}"
    )
    category = llmCategoriser.categorise(transaction["company_person"])
    if category == "ignore":
        name = transaction["company_person"].lower()
        bank_keywords = ["bank", "interest", "fee", "fees", "charge", "charges",
                        "atm", "transfer", "loan", "repayment", "interest"]
        if not any(k in name for k in bank_keywords):
            category = "misc"
    transaction["llm_category"] = (
        category  # Use different key to preserve original category
    )
    print(f"  → Category: {category}")

# Store as JSON output
output_dir = Path(__file__).parent / "categoriser" / "categorisedOutput"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "categorised_output.json"

with output_path.open("w", encoding="utf-8") as f:
    json.dump(cleanedTransactions, f, indent=2, ensure_ascii=False)

print(f"\n✅ Categorized transactions saved to: {output_path}")
print(f"Total transactions processed: {len(cleanedTransactions)}")
