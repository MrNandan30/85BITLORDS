import pandas as pd

def save_to_excel(data, out_path):
    rows = []
    for filename, bill in data:
        rows.append({
            'Filename': filename,
            'Date': bill.date,
            'Amount': bill.amount,
            'Provider': bill.provider,
            'Needs Review': bill.needs_review
        })
    df = pd.DataFrame(rows)
    df.to_excel(out_path, index=False)