"""
Quick setup helper — run once to verify your environment is correct.
Usage: python setup.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("\n🔍  Checking environment…\n")

checks = []

# 1. .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    checks.append(("✅", ".env file found"))
else:
    checks.append(("❌", ".env file NOT found — copy .env.example to .env and fill in your keys"))

# 2. API key
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key and api_key != "your_gemini_api_key_here":
    checks.append(("✅", f"GEMINI_API_KEY set ({api_key[:8]}…)"))
else:
    checks.append(("❌", "GEMINI_API_KEY is missing or still the placeholder value"))

# 3. Python version
major, minor = sys.version_info[:2]
if major == 3 and minor >= 10:
    checks.append(("✅", f"Python {major}.{minor} (>= 3.10 required)"))
else:
    checks.append(("⚠️ ", f"Python {major}.{minor} — recommend 3.10+"))

# 4. Key packages
packages = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("chromadb", "chromadb"),
    ("langchain_google_genai", "langchain-google-genai"),
    ("pydantic_settings", "pydantic-settings"),
    ("pandas", "pandas"),
    ("pypdf", "pypdf"),
    ("dotenv", "python-dotenv"),
]

for module, pkg in packages:
    try:
        __import__(module)
        checks.append(("✅", f"{pkg} installed"))
    except ImportError:
        checks.append(("❌", f"{pkg} NOT installed — run: pip install -r requirements.txt"))

# 5. Sample FAQ data
faq_path = os.path.join(os.path.dirname(__file__), "data", "sample_faqs.csv")
if os.path.exists(faq_path):
    import csv
    with open(faq_path, 'r', encoding='utf-8') as f:
        row_count = sum(1 for _ in csv.DictReader(f)) - 1  # Subtract header
    checks.append(("✅", f"sample_faqs.csv found ({row_count} rows)"))
else:
    checks.append(("❌", "data/sample_faqs.csv not found"))

# Print results
for icon, msg in checks:
    print(f"  {icon}  {msg}")

failed = [c for c in checks if c[0] == "❌"]
print()
if failed:
    print(f"  ⛔  {len(failed)} issue(s) found. Fix them before running the server.\n")
    sys.exit(1)
else:
    print("  🎉  All checks passed! Run the server with:\n")
    print("       uvicorn main:app --reload --port 8000\n")
    sys.exit(0)
