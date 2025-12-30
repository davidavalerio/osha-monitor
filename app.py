"""
OSHA Monitor - A comprehensive interface for OSHA regulatory updates
"""

from flask import Flask, render_template, request
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil import parser as date_parser

app = Flask(__name__)

# API and RSS sources
FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1/documents.json"
OSHA_INTERPRETATIONS_RSS = "https://www.osha.gov/laws-regs/standardinterpretations.xml"
OSHA_DIRECTIVES_RSS = "https://www.osha.gov/enforcement/directives.xml"


def format_time_ago(pub_date):
    """Convert a datetime to a human-readable 'time ago' string."""
    try:
        # Handle timezone-aware dates
        if pub_date.tzinfo is not None:
            pub_date = pub_date.replace(tzinfo=None)
        days_ago = (datetime.now() - pub_date).days
        if days_ago < 0:
            return "Upcoming"
        elif days_ago == 0:
            return "Today"
        elif days_ago == 1:
            return "Yesterday"
        elif days_ago < 7:
            return f"{days_ago} days ago"
        elif days_ago < 30:
            weeks = days_ago // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_ago < 365:
            months = days_ago // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            return pub_date.strftime("%b %Y")
    except:
        return ""


def fetch_federal_register(year=None, doc_types=None, limit=30):
    """Fetch OSHA documents from the Federal Register API."""
    if doc_types is None:
        doc_types = ["RULE", "PRORULE", "NOTICE"]

    params = {
        "conditions[agencies][]": "occupational-safety-and-health-administration",
        "conditions[type][]": doc_types,
        "fields[]": [
            "title",
            "type",
            "abstract",
            "publication_date",
            "effective_on",
            "html_url",
            "document_number",
            "pdf_url"
        ],
        "per_page": limit,
        "order": "newest"
    }

    if year and year != "all":
        try:
            params["conditions[publication_date][year]"] = int(year)
        except (ValueError, TypeError):
            pass

    try:
        response = requests.get(FEDERAL_REGISTER_API, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        documents = []
        for doc in data.get("results", []):
            processed = {
                "title": doc.get("title", ""),
                "abstract": doc.get("abstract", ""),
                "url": doc.get("html_url", ""),
                "pdf_url": doc.get("pdf_url", ""),
                "source": "Federal Register",
                "content_type": doc.get("type", ""),
            }

            # Parse publication date
            if doc.get("publication_date"):
                try:
                    pub_date = date_parser.parse(doc["publication_date"])
                    processed["pub_date"] = pub_date
                    processed["pub_date_formatted"] = pub_date.strftime("%B %d, %Y")
                    processed["time_ago"] = format_time_ago(pub_date)
                except:
                    processed["pub_date"] = None
                    processed["pub_date_formatted"] = doc["publication_date"]
                    processed["time_ago"] = ""

            # Parse effective date
            if doc.get("effective_on"):
                try:
                    eff_date = date_parser.parse(doc["effective_on"])
                    if eff_date > datetime.now():
                        days_until = (eff_date - datetime.now()).days
                        if days_until == 0:
                            processed["effective_status"] = "Effective today"
                        elif days_until == 1:
                            processed["effective_status"] = "Effective tomorrow"
                        elif days_until < 30:
                            processed["effective_status"] = f"Effective in {days_until} days"
                        else:
                            processed["effective_status"] = f"Effective {eff_date.strftime('%b %d, %Y')}"
                    else:
                        processed["effective_status"] = f"Effective since {eff_date.strftime('%b %d, %Y')}"
                except:
                    processed["effective_status"] = ""
            else:
                processed["effective_status"] = ""

            documents.append(processed)

        return documents, data.get("count", 0)

    except requests.RequestException as e:
        print(f"Error fetching Federal Register: {e}")
        return [], 0


def fetch_osha_rss(url, content_type, source_name):
    """Fetch and parse an OSHA RSS feed."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        documents = []

        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()
            pub_date_str = item.findtext("pubDate", "").strip()

            processed = {
                "title": title,
                "abstract": description,
                "url": link,
                "pdf_url": "",
                "source": source_name,
                "content_type": content_type,
                "effective_status": "",
            }

            # Parse publication date
            if pub_date_str:
                try:
                    pub_date = date_parser.parse(pub_date_str)
                    processed["pub_date"] = pub_date
                    processed["pub_date_formatted"] = pub_date.strftime("%B %d, %Y")
                    processed["time_ago"] = format_time_ago(pub_date)
                except:
                    processed["pub_date"] = None
                    processed["pub_date_formatted"] = ""
                    processed["time_ago"] = ""
            else:
                processed["pub_date"] = None
                processed["pub_date_formatted"] = ""
                processed["time_ago"] = ""

            documents.append(processed)

        return documents

    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []


def fetch_interpretations():
    """Fetch OSHA Letters of Interpretation."""
    return fetch_osha_rss(
        OSHA_INTERPRETATIONS_RSS,
        "Interpretation",
        "OSHA Interpretations"
    )


def fetch_directives():
    """Fetch OSHA Directives."""
    return fetch_osha_rss(
        OSHA_DIRECTIVES_RSS,
        "Directive",
        "OSHA Directives"
    )


@app.route("/")
def index():
    """Main page - show OSHA regulatory updates."""

    # Get filters from query params
    content_filter = request.args.get("content", "rules")
    year = request.args.get("year", str(datetime.now().year))

    # Fetch from all sources
    all_documents = []
    total_count = 0

    # Federal Register content
    if content_filter in ["all", "rules"]:
        fr_docs, fr_count = fetch_federal_register(
            year=year,
            doc_types=["RULE"],
            limit=30
        )
        all_documents.extend(fr_docs)
        total_count += fr_count

    if content_filter in ["all", "proposed"]:
        prop_docs, prop_count = fetch_federal_register(
            year=year,
            doc_types=["PRORULE"],
            limit=30
        )
        all_documents.extend(prop_docs)
        total_count += prop_count

    if content_filter in ["all", "notices"]:
        notice_docs, notice_count = fetch_federal_register(
            year=year,
            doc_types=["NOTICE"],
            limit=30
        )
        all_documents.extend(notice_docs)
        total_count += notice_count

    # OSHA website content (not filtered by year - RSS only has recent items)
    if content_filter in ["all", "interpretations"]:
        interp_docs = fetch_interpretations()
        # Filter by year if specified
        if year and year != "all":
            try:
                year_int = int(year)
                interp_docs = [d for d in interp_docs if d.get("pub_date") and d["pub_date"].year == year_int]
            except:
                pass
        all_documents.extend(interp_docs)
        total_count += len(interp_docs)

    if content_filter in ["all", "directives"]:
        directive_docs = fetch_directives()
        # Filter by year if specified
        if year and year != "all":
            try:
                year_int = int(year)
                directive_docs = [d for d in directive_docs if d.get("pub_date") and d["pub_date"].year == year_int]
            except:
                pass
        all_documents.extend(directive_docs)
        total_count += len(directive_docs)

    # Sort all documents by date (newest first)
    # Use a safe sort key that handles None and timezone-aware dates
    def sort_key(doc):
        pub_date = doc.get("pub_date")
        if pub_date is None:
            return datetime.min
        # Convert to naive datetime for comparison if needed
        if pub_date.tzinfo is not None:
            return pub_date.replace(tzinfo=None)
        return pub_date

    all_documents.sort(key=sort_key, reverse=True)

    # Group by content type for display
    final_rules = [d for d in all_documents if d.get("content_type") == "Rule"]
    proposed_rules = [d for d in all_documents if d.get("content_type") == "Proposed Rule"]
    notices = [d for d in all_documents if d.get("content_type") == "Notice"]
    interpretations = [d for d in all_documents if d.get("content_type") == "Interpretation"]
    directives = [d for d in all_documents if d.get("content_type") == "Directive"]

    today = datetime.now().strftime("%A, %B %d, %Y")
    current_year = datetime.now().year

    return render_template(
        "index.html",
        final_rules=final_rules,
        proposed_rules=proposed_rules,
        notices=notices,
        interpretations=interpretations,
        directives=directives,
        today=today,
        year=year,
        current_year=current_year,
        content_filter=content_filter,
        total_count=total_count,
        error=False
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
