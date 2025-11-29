from ocr.ocr import Ocr
from ocr.parser import OcrParser
import json

ocr_engine = Ocr()
# Replace with a valid image path or ensure the path exists
result = ocr_engine.perform_ocr('AUG 2025_20251126153531065.pdf')
# print(result)
# ocr_engine.print_result(result)
parser = OcrParser()
transactions = parser.parse_transactions(result)
print("=" * 80)
print("FINAL TRANSACTIONS:")
print(json.dumps(transactions, indent=2))
print("=" * 80)

# Also write to file for easier viewing
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("TRANSACTIONS:\n")
    f.write(json.dumps(transactions, indent=2))
print("Results written to output.txt")