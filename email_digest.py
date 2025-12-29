"""
Email digest for OSHA Monitor - sends daily alerts for new regulatory updates
"""

import os
import resend
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import parser as date_parser

# Configuration from environment variables
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "david@discern.earth")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "OSHA Monitor <alerts@discern.earth>")

# API sources
FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1/documents.json"
OSHA_INTERPRETATIONS_RSS = "https://www.osha.gov/laws-regs/standardinterpretations.xml"
OSHA_DIRECTIVES_RSS = "https://www.osha.gov/enforcement/directives.xml"


def fetch_recent_federal_register(days=1):
    """Fetch OSHA documents from the Federal Register published in the last N days."""

    cutoff_date = datetime.now() - timedelta(days=days)

    params = {
        "conditions[agencies][]": "occupational-safety-and-health-administration",
        "conditions[type][]": ["RULE", "PRORULE", "NOTICE"],
        "fields[]": [
            "title", "type", "abstract", "publication_date",
            "effective_on", "html_url", "pdf_url"
        ],
        "per_page": 50,
        "order": "newest"
    }

    try:
        response = requests.get(FEDERAL_REGISTER_API, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        documents = []
        for doc in data.get("results", []):
            if doc.get("publication_date"):
                try:
                    pub_date = date_parser.parse(doc["publication_date"])
                    if pub_date.replace(tzinfo=None) >= cutoff_date:
                        documents.append({
                            "title": doc.get("title", ""),
                            "type": doc.get("type", ""),
                            "abstract": doc.get("abstract", ""),
                            "url": doc.get("html_url", ""),
                            "pdf_url": doc.get("pdf_url", ""),
                            "pub_date": pub_date.strftime("%B %d, %Y"),
                            "effective_on": doc.get("effective_on", ""),
                            "source": "Federal Register"
                        })
                except:
                    pass

        return documents
    except Exception as e:
        print(f"Error fetching Federal Register: {e}")
        return []


def fetch_recent_rss(url, content_type, days=1):
    """Fetch recent items from an OSHA RSS feed."""

    cutoff_date = datetime.now() - timedelta(days=days)

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        documents = []

        for item in root.findall(".//item"):
            pub_date_str = item.findtext("pubDate", "").strip()
            if pub_date_str:
                try:
                    pub_date = date_parser.parse(pub_date_str)
                    if pub_date.replace(tzinfo=None) >= cutoff_date:
                        documents.append({
                            "title": item.findtext("title", "").strip(),
                            "type": content_type,
                            "abstract": item.findtext("description", "").strip(),
                            "url": item.findtext("link", "").strip(),
                            "pdf_url": "",
                            "pub_date": pub_date.strftime("%B %d, %Y"),
                            "effective_on": "",
                            "source": "OSHA.gov"
                        })
                except:
                    pass

        return documents
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []


def get_all_recent_documents(days=1):
    """Get all recent OSHA documents from all sources."""

    documents = []

    # Federal Register
    documents.extend(fetch_recent_federal_register(days))

    # OSHA RSS feeds
    documents.extend(fetch_recent_rss(
        OSHA_INTERPRETATIONS_RSS, "Interpretation", days
    ))
    documents.extend(fetch_recent_rss(
        OSHA_DIRECTIVES_RSS, "Directive", days
    ))

    return documents


def format_type_label(doc_type):
    """Convert document type to readable label."""
    labels = {
        "Rule": "Final Rule",
        "Proposed Rule": "Proposed Rule",
        "Notice": "Notice",
        "Interpretation": "Letter of Interpretation",
        "Directive": "Directive"
    }
    return labels.get(doc_type, doc_type)


def build_email_html(documents):
    """Build the HTML email content."""

    today = datetime.now().strftime("%A, %B %d, %Y")

    # Group by type
    final_rules = [d for d in documents if d["type"] == "Rule"]
    proposed = [d for d in documents if d["type"] == "Proposed Rule"]
    notices = [d for d in documents if d["type"] == "Notice"]
    interpretations = [d for d in documents if d["type"] == "Interpretation"]
    directives = [d for d in documents if d["type"] == "Directive"]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #1a365d; font-size: 24px; margin-bottom: 5px;">OSHA Monitor</h1>
        <p style="color: #666; margin-top: 0;">{today}</p>

        <p style="background: #f0f7ff; padding: 12px 16px; border-radius: 6px; border-left: 4px solid #3182ce;">
            <strong>{len(documents)} new item{'s' if len(documents) != 1 else ''}</strong> published since yesterday
        </p>
    """

    def render_section(title, items, color):
        if not items:
            return ""

        section = f"""
        <h2 style="color: {color}; font-size: 18px; margin-top: 30px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid {color};">
            {title} ({len(items)})
        </h2>
        """

        for doc in items:
            abstract = doc["abstract"][:300] + "..." if len(doc["abstract"]) > 300 else doc["abstract"]

            section += f"""
            <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee;">
                <a href="{doc['url']}" style="color: #2c5282; text-decoration: none; font-weight: 600; font-size: 16px;">
                    {doc['title']}
                </a>
                <p style="color: #666; font-size: 14px; margin: 8px 0;">
                    {abstract}
                </p>
                <p style="font-size: 13px; color: #888; margin: 0;">
                    Published {doc['pub_date']}
                    {f" · Effective {doc['effective_on']}" if doc['effective_on'] else ""}
                </p>
            </div>
            """

        return section

    html += render_section("Final Rules", final_rules, "#c53030")
    html += render_section("Proposed Rules", proposed, "#dd6b20")
    html += render_section("Letters of Interpretation", interpretations, "#2c7a7b")
    html += render_section("Directives", directives, "#5a67d8")
    html += render_section("Notices", notices, "#718096")

    html += f"""
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 13px; color: #888; text-align: center;">
            <a href="https://osha-monitor.onrender.com" style="color: #3182ce;">View all updates</a> ·
            Sent by OSHA Monitor
        </p>
    </body>
    </html>
    """

    return html


def build_email_text(documents):
    """Build plain text version of the email."""

    today = datetime.now().strftime("%A, %B %d, %Y")

    text = f"OSHA Monitor - {today}\n"
    text += "=" * 40 + "\n\n"
    text += f"{len(documents)} new item{'s' if len(documents) != 1 else ''} published since yesterday\n\n"

    for doc in documents:
        text += f"[{format_type_label(doc['type'])}] {doc['title']}\n"
        text += f"Published: {doc['pub_date']}\n"
        text += f"Link: {doc['url']}\n\n"

    text += "-" * 40 + "\n"
    text += "View all: https://osha-monitor.onrender.com\n"

    return text


def send_digest(days=1):
    """Fetch recent documents and send email digest."""

    if not RESEND_API_KEY:
        print("Error: RESEND_API_KEY not set")
        return False

    resend.api_key = RESEND_API_KEY

    # Get recent documents
    documents = get_all_recent_documents(days)

    if not documents:
        print("No new documents to report")
        return True

    # Build email content
    html_content = build_email_html(documents)
    text_content = build_email_text(documents)

    subject = f"OSHA Monitor: {len(documents)} new update{'s' if len(documents) != 1 else ''}"

    try:
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [ALERT_EMAIL],
            "subject": subject,
            "html": html_content,
            "text": text_content
        })
        print(f"Email sent successfully: {response}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


if __name__ == "__main__":
    # Run directly to send digest
    # LOOKBACK_DAYS env var allows manual test runs to look back further
    lookback = int(os.environ.get("LOOKBACK_DAYS", "1"))
    send_digest(days=lookback)
