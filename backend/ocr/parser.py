from typing import List, Dict, Any

class OcrParser:
    def __init__(self):
        pass

    def parse_transactions(self, ocr_result: List[Any]) -> List[Dict[str, Any]]:
        """
        Parses raw OCR result into a list of structured transactions.
        Handles both standard PaddleOCR format and PaddleX OCRResult objects.
        Starts from page 2 and stops when "End of Transaction Details" is detected.
        """
        transactions = []
        
        # Debug: Print the type and structure of ocr_result
        # print(f"OCR Result Type: {type(ocr_result)}")
        
        all_detections = []
        end_of_transactions_found = False
        
        # Handle PaddleX OCRResult objects
        if ocr_result and len(ocr_result) > 0:
            first_item = ocr_result[0]
            
            # Check if it's an OCRResult object (has rec_texts attribute)
            if hasattr(first_item, 'rec_texts') or (isinstance(first_item, dict) and 'rec_texts' in first_item):
                print("Detected PaddleX OCRResult format")
                
                # Process each page (OCRResult object), starting from page 2 (index 1)
                for page_idx, page in enumerate(ocr_result):
                    # Skip page 1 (index 0)
                    if page_idx == 0:
                        print(f"Skipping page {page_idx + 1} (non-transaction page)")
                        continue
                    
                    print(f"Processing page {page_idx + 1}")
                    
                    # Access attributes based on whether it's an object or dict
                    if hasattr(page, 'rec_texts'):
                        texts = page.rec_texts
                        polys = page.rec_polys
                        scores = page.rec_scores if hasattr(page, 'rec_scores') else [1.0] * len(texts)
                    else:
                        texts = page.get('rec_texts', [])
                        polys = page.get('rec_polys', [])
                        scores = page.get('rec_scores', [1.0] * len(texts))
                    
                    print(f"Found {len(texts)} text detections on page {page_idx + 1}")
                    
                    # Reconstruct standard format: [[box], (text, confidence)]
                    for i in range(len(texts)):
                        # Check if we've reached the end of transaction details
                        if "End of Transaction Details" in texts[i]:
                            print(f"Found 'End of Transaction Details' marker on page {page_idx + 1}")
                            end_of_transactions_found = True
                            break
                        
                        # Convert numpy array to list if needed
                        poly = polys[i].tolist() if hasattr(polys[i], 'tolist') else polys[i]
                        detection = [poly, (texts[i], scores[i])]
                        all_detections.append(detection)
                    
                    # Stop processing pages if end marker found
                    if end_of_transactions_found:
                        break
                        
            # Handle standard PaddleOCR list format
            elif isinstance(first_item, list):
                print("Detected standard PaddleOCR list format")
                # Start from page 2 (index 1)
                for page_idx, page in enumerate(ocr_result):
                    # Skip page 1 (index 0)
                    if page_idx == 0:
                        print(f"Skipping page {page_idx + 1} (non-transaction page)")
                        continue
                    
                    if page:
                        # Check for end marker in this page
                        for detection in page:
                            text = detection[1][0] if len(detection) > 1 else ""
                            if "End of Transaction Details" in text:
                                print(f"Found 'End of Transaction Details' marker on page {page_idx + 1}")
                                end_of_transactions_found = True
                                break
                            all_detections.append(detection)
                        
                        if end_of_transactions_found:
                            break
            else:
                print(f"Unknown OCR result format: {type(first_item)}")
                return []

        if not all_detections:
            print("No detections found!")
            return []

        # Debug: Check the structure of detections
        print(f"Total detections across all pages: {len(all_detections)}")
        if all_detections:
            print(f"First detection: {all_detections[0]}")
            print(f"Sample texts: {[d[1][0] for d in all_detections[:5]]}")

        # 1. Sort by Y coordinate to process top-to-bottom
        # box is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        # We use the top-left y (y1) for sorting
        try:
            all_detections.sort(key=lambda x: x[0][0][1])
            print("Successfully sorted detections by Y coordinate")
        except (IndexError, TypeError) as e:
            print(f"Error sorting detections: {e}")
            print(f"Detection structure issue - cannot access x[0][0][1]")
            return []

        # 2. Group into lines
        lines = self._group_into_lines(all_detections)

        # 3. Extract data from lines
        # This is a heuristic approach. You might need to adjust based on the specific bank statement format.
        for line in lines:
            transaction = self._parse_line(line)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _group_into_lines(self, detections, y_threshold=10):
        """
        Groups detections into lines based on Y-coordinate proximity.
        """
        lines = []
        current_line = []
        
        if not detections:
            return lines

        # Initialize with the first detection
        current_line.append(detections[0])
        
        for i in range(1, len(detections)):
            current_det = detections[i]
            prev_det = current_line[-1]
            
            # Compare Y-center or Top-Y
            curr_y = current_det[0][0][1]
            prev_y = prev_det[0][0][1]
            
            if abs(curr_y - prev_y) <= y_threshold:
                current_line.append(current_det)
            else:
                # Sort current line by X coordinate (left to right)
                current_line.sort(key=lambda x: x[0][0][0])
                lines.append(current_line)
                current_line = [current_det]
        
        # Append the last line
        if current_line:
            current_line.sort(key=lambda x: x[0][0][0])
            lines.append(current_line)
            
        return lines

    def _parse_line(self, line) -> Dict[str, Any]:
        """
        Attempts to parse a single line of text into a transaction.
        Expected format example: Date Description Amount
        """
        # Combine text in the line
        texts = [det[1][0] for det in line]
        full_text = " ".join(texts)        

        return {
            "raw_text": full_text,
            "parts": texts
        }
