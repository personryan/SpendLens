from paddleocr import PaddleOCR

class Ocr:
    def __init__(self):
        # Initialize PaddleOCR with English language
        self.ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

    def perform_ocr(self, image_path):
        result = self.ocr_model.ocr(image_path)
        print(f"OCR Result type: {type(result)}")
        print(f"OCR Result length: {len(result) if result else 0}")
        if result and len(result) > 0:
            print(f"First page type: {type(result[0])}")
            print(f"First page attributes: {dir(result[0])}")
            # OCRResult objects have different attributes, let's inspect them
            first_page = result[0]
            if hasattr(first_page, '__dict__'):
                print(f"First page dict: {first_page.__dict__}")
            if hasattr(first_page, 'rec_texts'):
                print(f"Has rec_texts: {len(first_page.rec_texts)} items")
            if hasattr(first_page, 'dt_polys'):
                print(f"Has dt_polys: {len(first_page.dt_polys)} items")
        return result

    def print_result(self, result):
        if not result or result[0] is None:
            print("No text detected.")
            return
            
        for line in result:
            for word_info in line:
                # word_info is a tuple/list where the last element is the text
                print(word_info[-1])