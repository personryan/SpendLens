from ocr.ocr import Ocr
from ocr.parser import OcrParser
from datetime import datetime
from pathlib import Path
import json
from categoriser.sorter import OcrSorter

ocr_engine = Ocr()
# Replace with a valid image path or ensure the path exists
result = ocr_engine.perform_ocr('bankStatements/AUG 2025_20251126153531065.pdf')
# print(result)
# ocr_engine.print_result(result)
parser = OcrParser()
transactions = parser.parse_transactions(result)
# print("=" * 80)
# print("FINAL TRANSACTIONS:")
# print(json.dumps(transactions, indent=2))
# print("=" * 80)

# Write to JSON file for easier data manipulation
output_dir = Path(__file__).parent / "ocr" / "ocrOutput"
output_dir.mkdir(parents=True, exist_ok=True)

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = output_dir/"output.json"

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


