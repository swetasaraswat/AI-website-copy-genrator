#!/usr/bin/env python3
"""
generate_prompt.py

Fills a prompt template from prompts/ with the details of a business from
businesses/ and prints the finished prompt. Optionally sends it to Gemini.

Examples:
    python generate_prompt.py --list
    python generate_prompt.py -b salon -t homepage
    python generate_prompt.py -b cafe -t service_page -s "Small event bookings"
    python generate_prompt.py -b clinic -t cta --save
    python generate_prompt.py -b salon -t homepage --run --save
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT / "prompts"
BUSINESSES_DIR = ROOT / "businesses"
OUTPUT_DIR = ROOT / "output"

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def list_names(folder, suffix):
    """Names (without extension) of the files in a folder. Files starting with _ are skipped."""
    return sorted(
        p.stem for p in folder.glob(f"*{suffix}") if not p.stem.startswith("_")
    )


def load_business(name):
    """Load a business by short name (salon) or by path to a JSON file."""
    path = Path(name)
    if not path.suffix:
        path = BUSINESSES_DIR / f"{name}.json"
    if not path.exists():
        available = ", ".join(list_names(BUSINESSES_DIR, ".json"))
        sys.exit(f"Business file not found: {path}\nAvailable: {available}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_template(name):
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        available = ", ".join(list_names(PROMPTS_DIR, ".md"))
        sys.exit(f"Template not found: {path}\nAvailable: {available}")
    return path.read_text(encoding="utf-8")


def as_text(value):
    """Lists become an indented bullet list. Everything else becomes a plain string."""
    if isinstance(value, list):
        return "\n".join(f"  - {item}" for item in value)
    return str(value)


def fill_template(template, data):
    """Replace every {{placeholder}} in the template with its value from data."""
    values = {key: as_text(value) for key, value in data.items()}
    missing = sorted({name for name in PLACEHOLDER.findall(template) if name not in values})
    if missing:
        raise ValueError("Missing values for: " + ", ".join(missing))
    return PLACEHOLDER.sub(lambda match: values[match.group(1)], template)


def build_prompt(business, template_name, service=None):
    """Combine a business dict and a template into the final prompt text."""
    data = dict(business)
    if service is None:
        services = business.get("services") or [""]
        service = services[0]
    data["service_name"] = service
    return fill_template(load_template(template_name), data)


def run_gemini(prompt):
    """Send the prompt to Gemini's REST API (standard library only) and return the text."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Set the GEMINI_API_KEY environment variable first (see README).")
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
    except urllib.error.HTTPError as err:
        sys.exit(f"Gemini API error {err.code}: {err.read().decode('utf-8', 'replace')[:300]}")
    except urllib.error.URLError as err:
        sys.exit(f"Could not reach the Gemini API: {err.reason}")
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        sys.exit("Unexpected response from Gemini: " + json.dumps(data)[:300])


def save(text, filename):
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(text, encoding="utf-8")
    print(f"Saved to {path}", file=sys.stderr)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description="Build prompts for website copy.")
    parser.add_argument("-b", "--business", help="business name (see --list) or path to a JSON file")
    parser.add_argument("-t", "--template", help="template name (see --list)")
    parser.add_argument("-s", "--service", help="service to write about (service_page template only)")
    parser.add_argument("--run", action="store_true", help="send the prompt to Gemini and print the result")
    parser.add_argument("--save", action="store_true", help="save the prompt (and the result, with --run) to output/")
    parser.add_argument("--list", action="store_true", help="show available businesses and templates")
    args = parser.parse_args()

    if args.list:
        print("Businesses:", ", ".join(list_names(BUSINESSES_DIR, ".json")))
        print("Templates: ", ", ".join(list_names(PROMPTS_DIR, ".md")))
        return
    if not args.business or not args.template:
        parser.error("both --business and --template are required (or use --list)")

    business = load_business(args.business)
    if args.service and args.service not in business.get("services", []):
        print(f"Note: '{args.service}' is not in this business's services list.", file=sys.stderr)

    try:
        prompt = build_prompt(business, args.template, args.service)
    except ValueError as err:
        sys.exit(f"Could not fill the template. {err}")

    base = f"{Path(args.business).stem}_{args.template}"
    if args.template == "service_page":
        base += "_" + slug(args.service or business["services"][0])

    if args.save:
        save(prompt, f"{base}_prompt.md")

    if args.run:
        result = run_gemini(prompt)
        print(result)
        if args.save:
            save(result, f"{base}_output.md")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
