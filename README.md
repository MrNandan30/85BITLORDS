📄 Bill Manager — Gen AI Bill Entry & Categorization Web App
This project is a Flask-based web application that lets users upload bill files (PDFs/images), auto-extracts important data using Gen AI and fallback OCR, and organizes them by category. It includes manual fallback for missing data, supports custom categories, and allows Excel export per category.

🎯 Ideal for anyone looking to digitize and organize utility or shopping bills with AI assistance.

🔧 Features:

📥 Drag-and-drop or multi-file upload

🧠 Auto-extraction of date, amount, provider from filenames

🤖 AI-based categorization (gas, electricity, groceries, hospital, misc)

📝 Manual correction popup for missing/uncertain fields

📂 Categorized views of bills (month-wise)

📊 Excel export by category

🗑 Row-level delete for bill entries..

📁 Project Structure

bill_manager/
├── app.py
├── extractor.py
├── excel_writer.py
├── db_utils.py (optional if separated later)
├── templates/
│   ├── index.html
│   └── category_view.html
├── static/
│   ├── script.js
│   └── style.css
├── uploads/         # Uploaded bills
├── output/          # Excel downloads
├── bills.db         # SQLite database (auto-generated)
└── README.md
