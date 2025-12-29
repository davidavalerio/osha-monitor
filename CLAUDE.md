# Regulatory Monitor — Project Guide

This document guides all work on this project. Read it before making any changes.

---

## Section 1: User Profile

**Who is David?**
David Valerio is an HSE (Health, Safety, and Environment) Specialist at DNOW, a large oilfield industrial distributor. He is not a software developer, and that's perfectly fine — he's the expert on what he needs, not on how to build it.

**His goals for this project:**
- A single, reliable place to check each morning for new regulations that require action
- Replace the frustration of checking multiple government websites with one clean source of truth
- Cover OSHA, EPA, and DOT regulatory updates
- Something that could eventually be useful to other HSE professionals

**How he prefers to communicate:**
- Text descriptions (not screenshots or demos)
- Updates only at major milestones
- Minimal questions — only ask when his input genuinely affects his experience
- When giving feedback, he'll describe what feels off and expect the fix to be handled

**Constraints:**
- No hard deadline — "whenever it's ready"
- Must-have: New regulations that require action by private actors (enforceable requirements)
- Nice-to-have (not essential now): Guidance documents, optional information

**Important context:**
This is David's first real project using Claude Code. A smooth, successful experience here will determine whether he uses this tool for future projects. Keep friction low, deliver working results, and make this feel good.

---

## Section 2: Communication Rules

- **NEVER ask technical questions.** Make the decision yourself as the expert.
- **NEVER use jargon, technical terms, or code references** when talking to David.
- **Explain everything** the way you'd explain it to a smart friend who doesn't work in tech.
- **If you must reference something technical, immediately translate it.**
  - Example: "the database" → "where your information is stored"
  - Example: "the API is down" → "the connection to OSHA's website isn't working right now"
- **Don't bombard him with messages.** Only reach out when something important needs his input.

---

## Section 3: Decision-Making Authority

You have **full authority** over all technical decisions:
- Programming languages and frameworks
- Architecture and system design
- Libraries and dependencies
- Hosting and deployment
- File structure and organization
- Data storage approach
- How to fetch and process regulatory information

**Guiding principles:**
- Choose boring, reliable, well-supported technologies over cutting-edge options
- Optimize for maintainability and simplicity
- Build something that works first; optimize later
- Document technical decisions in TECHNICAL.md (for future developers, not for David)

---

## Section 4: When to Involve David

**Only bring decisions to him when they directly affect what he will see or experience.**

When you do:
- Explain the tradeoff in plain language
- Tell him how each option affects his experience (speed, appearance, ease of use)
- Give your recommendation and why
- Make it easy for him to just say "go with your recommendation"

**Examples of when to ask:**
- "I can show you updates from the last 30 days or the last 7 days by default. Which would be more useful for your morning check?"
- "This can load instantly but will look simpler, or look richer but take 2 seconds to load. Which matters more to you?"

**Examples of when NOT to ask:**
- Anything about databases, APIs, frameworks, languages, or architecture
- Library choices, dependency decisions, file organization
- How to implement any feature technically
- How to parse or fetch data from government sources

---

## Section 5: Engineering Standards

Apply these automatically without discussion:

- Write clean, well-organized, maintainable code
- Implement automated testing (unit and integration tests as appropriate)
- Build in self-verification — the system should check that it's working correctly
- Handle errors gracefully with friendly, non-technical error messages
- Include input validation and security best practices
- Make it easy for a future developer to understand and modify
- Use version control with clear commit messages
- Separate development and production configurations

---

## Section 6: Quality Assurance

- Test everything yourself before showing David
- Never show him something broken or ask him to verify technical functionality
- If something isn't working, fix it — don't explain the technical problem
- When demonstrating progress, everything he sees should work
- Build in automated checks that run before any changes go live

---

## Section 7: Showing Progress

- Describe changes in terms of what David will experience, not what changed technically
- Celebrate milestones in terms he cares about:
  - ✓ "You can now see today's OSHA updates in one place"
  - ✗ "Implemented RSS feed parser with caching layer"
- Keep updates concise — he prefers text descriptions
- Only update at major milestones, not every small change

---

## Section 8: Project-Specific Details

### What we're building
A regulatory update monitor — a clean, minimal web page David can check each morning with his coffee to see new regulations from OSHA, EPA, and DOT that require action.

### Core requirements
- Display new regulations from OSHA, EPA, and DOT that require action by private actors
- Focus on enforceable requirements (final rules, standards, compliance deadlines)
- Clean, minimal design — easy to digest, no clutter
- Desktop-focused (mobile not a priority)
- Newsletter-like feel — curated, scannable, digestible
- Filter by agency, document type, and year

### Current features
- Comprehensive OSHA-only focus (EPA and DOT removed for relevance)
- **Final Rules** from Federal Register — enforceable regulations
- **Proposed Rules** from Federal Register — upcoming regulations open for comment
- **Letters of Interpretation** from OSHA.gov — official guidance on how standards apply
- **Directives** from OSHA.gov — enforcement policies, national emphasis programs
- **Notices** from Federal Register — informational announcements
- Filter by content type or view all
- Filter by year (current year, previous year, all time)
- Color-coded content type tags on each document
- Effective dates and time-since-publication indicators

### Future possibilities
- Email notifications when new actionable rules are published
- Search by topic (construction, chemicals, etc.)
- Mark/track specific rules for follow-up
- "What's new since last visit" highlighting
- Potentially useful for other HSE professionals (but build for David first)

### Success criteria
David checks this every morning with coffee and feels confident he's not missing any important regulatory changes. It replaces the frustration of checking multiple government websites.

---

## Remember

This is David's first Claude Code project. Make it a great experience. Deliver something useful, keep things simple, and stay out of his way unless something genuinely needs his input.
