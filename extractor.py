import re
from collections import namedtuple

BillData = namedtuple('BillData', ['date', 'amount', 'provider', 'needs_review'])

def extract_data_from_text(text: str) -> BillData:
    text = text.replace('\n', ' ').replace('\r', '').lower()
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', text)
    date = date_match.group(1) if date_match else "-"
    amount = "-"
    needs_review = False

    keywords = ["final price", "amount paid", "net payable", "grand total", "total"]
    for k in keywords:
        pattern = rf'{k}[^0-9\-]*([\d,]+\.\d{{1,2}})'
        match = re.search(pattern, text)
        if match:
            amount = match.group(1).replace(',', '')
            break

    if amount == "-":
        matches = re.findall(r'(\d{3,7}\.\d{1,2})', text)
        if matches:
            amount = max(matches, key=lambda x: float(x))
        else:
            needs_review = True

    provider_match = re.search(r'(yeshaswini|bescom|indian oil|bharat gas|reliance)', text)
    provider = provider_match.group(1).upper() if provider_match else "-"
    if provider == "-":
        needs_review = True

    return BillData(date, amount, provider, needs_review)

def extract_data_from_file(file_path):
    import fitz
    import pytesseract
    from PIL import Image
    import io

    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        if len(text.strip()) < 30:
            raise Exception("Too little text")
    except:
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text += pytesseract.image_to_string(img)
        doc.close()
    
    return extract_data_from_text(text)

def auto_categorize(bill: BillData) -> str:
    provider = bill.provider.lower()
    if "gas" in provider:
        return "Gas"
    if "bescom" in provider:
        return "Electricity"
    if "hospital" in provider:
        return "Hospital"
    if "bazaar" in provider or "mart" in provider:
        return "Groceries"
    return "Misc"