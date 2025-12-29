# Technical Documentation

This file documents technical decisions for future developers. Not intended for the end user.

## Architecture Overview

Simple Python web application that fetches OSHA regulatory updates from the Federal Register API and displays them in a clean web interface.

## Technology Choices

### Backend: Python + Flask
- **Why Python**: Widely supported, easy to maintain, excellent for data fetching/processing
- **Why Flask**: Minimal, mature, well-documented, no unnecessary complexity

### Data Source: Federal Register API
- **Endpoint**: `https://www.federalregister.gov/api/v1/documents.json`
- **No authentication required**: Public API, no API keys needed
- **Filtering**: By agency (OSHA) and document type (RULE, PRORULE for proposed rules)
- **Documentation**: https://www.federalregister.gov/developers/documentation/api/v1

### Frontend: Plain HTML + CSS
- No JavaScript frameworks
- Minimal, readable CSS
- Focus on content legibility and fast loading

## API Query Parameters

```
conditions[agencies][]=occupational-safety-and-health-administration
conditions[type][]=RULE         # Final rules (enforceable)
conditions[type][]=PRORULE      # Proposed rules (coming soon)
fields[]=title
fields[]=type
fields[]=abstract
fields[]=publication_date
fields[]=effective_on
fields[]=html_url
fields[]=document_number
per_page=20
```

## Document Types

- **RULE**: Final rules - enforceable regulations
- **PRORULE**: Proposed rules - upcoming regulations open for comment
- **NOTICE**: General notices - informational only (not included by default)

## Deployment

- Local development: `flask run` or `python app.py`
- Production: Use gunicorn with `gunicorn app:app`

## File Structure

```
osha_monitor/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Main display template
├── static/
│   └── style.css       # Minimal styling
├── requirements.txt    # Python dependencies
├── CLAUDE.md          # Project guide (for AI assistant)
└── TECHNICAL.md       # This file (for developers)
```

## Future Expansion

To add EPA or DOT:
- Add agency slugs to API query: `environmental-protection-agency`, `transportation-department`
- Update filtering UI to allow agency selection
- Consider caching if API calls become slow
