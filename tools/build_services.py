#!/usr/bin/env python3
"""
Builds every individual service page and the service navigation from one
source of truth (CATALOG below).

Run from the project root after editing the catalog or the templates:

    python3 tools/build_services.py

It will:
  * (re)write services/<slug>.html for every service, deleting pages for
    services that were removed from the catalog;
  * fill the <!-- services-menu:* --> mega-menu markers in index.html,
    about.html and contact.html;
  * fill the <!-- services-directory:* --> homepage section in index.html;
  * fill the <!-- footer-services:* --> footer list on all root pages.

Only the content between markers is replaced, so the rest of each root
page can be edited by hand as before.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"
SITE_URL = "https://www.hastenbusinesssolutions.com/"  # placeholder, same as the root pages

# --------------------------------------------------------------------------
# Catalog: category -> sub-group -> services
# --------------------------------------------------------------------------

CATALOG = [
    {
        "name": "Startup",
        "key": "startup",
        "icon": "rocket-takeoff",
        "blurb": "Register your business, secure licences and get certified.",
        "groups": [
            ("Business Registration", [
                "Company Registration", "LLP Registration", "Public Limited Company Registration",
                "One Person Company Registration", "Partnership Firm Registration",
                "Sole Proprietorship Registration", "Nidhi Company Registration",
                "Producer Company Registration", "Indian Subsidiary Company Registration",
                "Startup India Registration",
            ]),
            ("NGO / Trust", [
                "NGO Registration", "80G and 12A Registration", "Section 8 Company Registration",
                "Society Registration", "FCRA Registration", "12AA Registration", "Trust Registration",
                "12AB Registration", "Strike off Section 8 Companies", "NGO CSR-1 Filing",
                "NGO CSR Consultancy", "NGO Income Tax Advisory", "NGO Accounting",
                "NGO Project Report", "Trust Annual Compliance", "NGO Darpan Registration",
                "80G Registration",
            ]),
            ("Government Licenses", [
                "Shop & Establishment License", "CE Certification", "PSARA License", "Trade License",
                "Health Trade License", "Factory License", "FDA Certification", "GMP Certification",
                "AYUSH License", "WPC Certification", "PESO Certification", "CAPEXIL Certificate",
                "TEC Certification", "CLRA Registration and Licensing", "REACH Registration",
                "NASSCOM Membership", "IP-1 License in India", "FIFP Approval for Telecom",
                "Homologation Certificate", "Vehicle Type Approval Certificate",
                "IMEI Number Registration", "IMEI Certificate for Import of Mobile Handsets",
                "GJEPC Certificate", "RDSO Vendor Registration", "Khadi Board Registration",
            ]),
            ("Government Registration", [
                "MSME Registration", "IEC Registration", "EPF Registration", "RERA Registration",
                "NSIC Registration", "ESI Registration", "FIEO Registration", "Building NOC",
                "RERA Registration for Agents", "RERA Registration for Promoters",
                "APEDA Registration", "RNI Registration", "BEE Certification",
                "Spice Board Registration", "Barcode Registration",
                "World Manufacturer Identifier (WMI) Code", "Sanitary Import Permit",
                "NPOP Certification", "Coconut Board Registration", "Drone Registration",
                "IEC Code Renewal", "Political Party Registration", "MSME Return Filing",
                "Financial Intelligence Unit Registration", "GSP Certificate", "GACC Registration",
                "NABL Accreditation",
            ]),
            ("ISO Certifications", [
                "ISO Registration", "ISO 14001 EMS", "ISO 22000 FSMS", "ISO 9001:2015",
                "ISO 50001", "ISO 45001", "ISO 20000", "ISO 31000", "ISO 13485",
                "ISO 21101:2014", "ISO 37001:2016", "ISO 27001 ISMS", "ISO 16001", "ISO 39001",
                "ISO 2768-1",
            ]),
            ("FSSAI & Eating License", [
                "FSSAI License", "FSSAI License Renewal", "FSSAI State License",
                "Eating House License", "FSSAI Central License", "FSSAI Annual Return",
                "FSSAI Product Approval", "Food Recycling License", "FPO Mark Certification",
            ]),
        ],
    },
    {
        "name": "IP & Trademark",
        "key": "ip-trademark",
        "icon": "shield-lock",
        "blurb": "Protect your brand, designs, inventions and creative work.",
        "groups": [
            ("Trademarks India", [
                "Trademark Registration", "Trademark Objection", "Trademark Assignment",
                "Trademark Rectification", "Intellectual Property Dispute", "Trademark Renewal",
                "Trademark Classes Finder", "Trademark Hearing", "Trademark Opposition",
                "Trademark Search", "Brand Name Registration", "Logo Registration",
                "Wordmark Registration", "IP Risk Assessment Reports",
            ]),
            ("International TM", ["International Trademark Registration"] + [
                "Trademark Registration in " + country for country in (
                    "USA", "Mauritius", "Dubai", "France", "Singapore", "UK", "Luxembourg",
                    "Indonesia", "Poland", "Japan", "Germany", "Sri Lanka", "Egypt",
                )
            ]),
            ("Designs", ["Design Registration", "Design Registration Renewal"]),
            ("GI", ["Registration of Geographical Indication (GI)", "GI Enforcement Service"]),
            ("Advisory", ["Patent Due Diligence", "IP Valuation Services"]),
            ("TM Watch", ["Trademark Watch Services", "Trademark Monitoring"]),
            ("Copyright", [
                "Copyright Registration", "Copyright Disclaimer", "Copyright Objection",
                "Copyright Assignment",
            ]),
            ("Patent", [
                "Patent Registration", "Indian Patent Search", "Patent Opposition",
                "Patent Revocation",
            ]),
        ],
    },
    {
        "name": "Compliance",
        "key": "compliance",
        "icon": "clipboard-check",
        "blurb": "Stay compliant with ROC, tax, accounting and legal requirements.",
        "groups": [
            ("Secretarial", [
                "Winding Up of Private Limited Company", "Closing a Limited Liability Partnership",
                "Annual Compliance of a Pvt. Ltd. Company", "Annual Filing for LLP",
                "Event Based Compliances in a Company", "Change in Object Clause",
                "Appointment and Resignation of Directors", "Change in Name Clause",
                "Removal of Director", "Nidhi Company Compliance", "Section 8 Company Compliance",
                "NBFC Compliance", "Change in Registered Office", "Change in Share Capital",
                "Revival of Struck Off Companies", "MCA Compliance", "Change in Directors",
                "Change in LLP Agreement", "Liquidation of Company", "AGR-Return Filing",
                "Form AOC-4", "Form MGT-7", "SPICe+ Form", "AGILE PRO S",
                "Payment Gateway Compliance", "Insurance Broker Compliance",
                "NBFC Account Aggregator Compliance", "Insurance Web Aggregator Compliance",
            ]),
            ("Tax Filing/Compliance", [
                "GST Registration", "GST Return Filing", "TDS Return Filing",
                "Professional Tax Registration", "Income Tax Return Filing",
                "GST Advisory Services", "GST Annual Return Filing", "GST LUT Form",
                "GST Compliance Services", "Income Tax Compliance", "Income Tax Advisory",
                "XBRL Filing", "GST Registration for NRI", "CA Consultation Services",
                "Company Secretarial Services", "Income Tax Notice Management Software",
                "GST Notice Management Software", "ITR for NRI",
                "Green Bonds & Sustainable Finance Advisory",
                "MCA Compliance for Insurance Company", "Money Changer Compliance",
                "GST Consultant",
            ]),
            ("Accounting & CFO", [
                "Due Diligence", "Business Plan", "Virtual CFO Services", "Accounts Payable Service",
                "Accounts Receivable Services", "Tax Audit", "Forensic Audit",
                "Bookkeeping Services", "Fundraising Services", "Term Sheet", "Manufacturing Audit",
                "Technical Audit", "Factory Sanitation Audit", "M2M Communications",
                "Ethical Audits", "Insurance Audit", "Fractional CFO Services", "MIS Reporting",
            ]),
            ("Contracts & Agreements", [
                "Service Level Agreement", "Share Purchase Agreement", "Franchise Agreement",
                "Sale Deed Registration", "Gift Deed", "Residential Rental Agreement",
                "Commercial Rental Agreement", "Relinquishment Deed", "Probate of Will",
                "Shareholders’ Agreement", "Joint Venture Agreement",
            ]),
            ("Legal Services", [
                "Legal Notice", "RERA Complaint", "Cheque Bounce Notice", "Caveat Petition",
                "Legal Heir Certificate", "Section 8-Demand Notice", "Succession Certificate",
                "Lease Agreement Drafting", "Will Drafting", "Power of Attorney (POA)",
                "Legal Notice for Defamation", "Online Dispute Resolution",
                "Online Legal India Services", "Company Dispute Resolution",
                "Consumer Dispute Resolution", "POSH Compliance Services",
            ]),
            ("Convert Your Business", [
                "Secretarial Audit", "Sole Proprietorship to Pvt. Ltd. Company",
                "Pvt. Ltd. to Public Limited", "LLP to Private Company",
                "Partnership Firm to Pvt. Ltd. Company", "OPC to Private Limited Company",
            ]),
        ],
    },
]

# Footer "Services" column: a short list of the most-requested pages.
FOOTER_SERVICES = [
    "Company Registration", "GST Registration", "Income Tax Return Filing",
    "Trademark Registration", "Bookkeeping Services", "ISO 9001:2015",
]

# --------------------------------------------------------------------------
# Shared copy per sub-group. {name} is replaced with the service name.
# --------------------------------------------------------------------------

IMAGES = {
    "virtual-accounting": "Accountant reviewing financial documents and using a calculator",
    "taxation-planning": "Professional reviewing tax and planning documents at a desk",
    "gst-services": "Financial documents and a calculator on a desk",
    "corporate-compliance": "Business professional handing over a signed document",
    "auditing": "Magnifying glass reviewing printed financial charts",
    "financial-reporting": "Magnifying glass reviewing a page of financial reporting charts",
    "trademark": "Professional signing a registration document",
    "virtual-operations": "Business team collaborating at their desks in a modern office",
}

GROUP_COPY = {
    "Business Registration": dict(
        icon="building-add", image="corporate-compliance",
        lede="{name}, handled end to end — from name approval and paperwork to filing and your certificate.",
        overview=[
            "Choosing the right structure and registering it correctly is the foundation every later compliance sits on. We guide you through {name}, explain what the structure means for ownership, liability and tax, and prepare every document the registrar expects.",
            "We stay with the application until approval, then hand over a clear list of the next steps — bank account, PAN and TAN, GST and first-year filings — so nothing is missed after day one.",
        ],
        includes=[
            "Consultation on eligibility and the right structure",
            "Name availability check and reservation",
            "Drafting of incorporation documents",
            "Filing with the relevant authority and follow-up",
            "Post-registration compliance checklist",
        ],
    ),
    "NGO / Trust": dict(
        icon="heart", image="virtual-operations",
        lede="{name} for your non-profit, prepared by a team that works with NGOs and trusts regularly.",
        overview=[
            "Non-profits face their own set of registrations, exemptions and annual obligations, and a gap in any of them can affect donations and tax benefits. We handle {name} with close attention to what regulators scrutinise most: objects, governance and the use of funds.",
            "Alongside the filing, we help you set up the records and reporting habits that make renewals and audits straightforward later.",
        ],
        includes=[
            "Review of your trust deed, MoA or bye-laws",
            "Preparation of the application and supporting documents",
            "Filing and liaison with the department",
            "Responses to queries and clarifications",
            "Guidance on ongoing reporting and renewals",
        ],
    ),
    "Government Licenses": dict(
        icon="patch-check", image="corporate-compliance",
        lede="Get {name} without guessing at the requirements — we map what applies, prepare the file and track it to approval.",
        overview=[
            "Licences and certifications are often a precondition for operating, importing or selling a product, and each authority has its own forms, inspections and timelines. We assess how {name} applies to your business and put together an application that answers the authority's questions up front.",
            "Once it is issued, we note renewal dates and conditions so the licence stays valid as your operations grow.",
        ],
        includes=[
            "Assessment of applicability for your business",
            "Document and technical file preparation",
            "Application filing with the authority",
            "Coordination for inspections or testing where required",
            "Renewal and condition tracking",
        ],
    ),
    "Government Registration": dict(
        icon="bank", image="corporate-compliance",
        lede="{name} done correctly the first time, with documents prepared and filed by our team.",
        overview=[
            "Government registrations unlock schemes, benefits and the right to trade in certain sectors — but only when your details match across every record. We handle {name} from the eligibility check to the certificate, cross-checking your data against PAN, GST and incorporation records.",
            "We also explain exactly what the registration requires of you afterwards, from periodic returns to renewals.",
        ],
        includes=[
            "Eligibility check and document list",
            "Verification of data across your existing records",
            "Application preparation and submission",
            "Follow-up until the certificate is issued",
            "Explanation of post-registration obligations",
        ],
    ),
    "ISO Certifications": dict(
        icon="award", image="auditing",
        lede="Prepare for {name} with a clear gap analysis, documentation support and audit readiness.",
        overview=[
            "ISO certification shows customers and tender committees that your processes meet an international standard. For {name}, we review your current processes against the standard's clauses, identify the gaps and help you build the documentation and controls the certification body will audit.",
            "We coordinate with an accredited certification body and support you through the audit and any corrective actions it raises.",
        ],
        includes=[
            "Gap analysis against the standard",
            "Policy, procedure and manual documentation",
            "Internal audit and management review support",
            "Coordination with the certification body",
            "Surveillance audit and renewal support",
        ],
    ),
    "FSSAI & Eating License": dict(
        icon="cup-hot", image="gst-services",
        lede="Food business compliance made simple — {name} prepared, filed and tracked by our team.",
        overview=[
            "Every food business needs the right licence category, and choosing the wrong one or filing incomplete documents are the most common reasons for rejection. We look at your turnover, activity and premises to handle {name} under the correct category.",
            "We also keep track of renewals and annual returns so your licence never lapses.",
        ],
        includes=[
            "Licence category assessment",
            "Document checklist and preparation",
            "Application filing on the relevant portal",
            "Query responses and inspection support",
            "Renewal and annual return reminders",
        ],
    ),
    "Trademarks India": dict(
        icon="r-circle", image="trademark",
        lede="Protect your brand in India with {name}, followed through the Trade Marks Registry by our team.",
        overview=[
            "A brand name or logo is often a business's most valuable asset, and protecting it depends on getting class selection, descriptions and responses right. We handle {name} with a search-first approach, so you understand the risks before you file or respond.",
            "We track every stage on the Registry portal and keep you informed of deadlines, hearings and next steps.",
        ],
        includes=[
            "Search and risk assessment",
            "Class and specification drafting",
            "Filing, replies and documentation",
            "Hearing and deadline tracking",
            "Status updates until the matter is closed",
        ],
    ),
    "International TM": dict(
        icon="globe2", image="trademark",
        lede="Extend your brand protection abroad with {name}, through the Madrid Protocol or a direct national filing.",
        overview=[
            "Entering a new market without trademark protection leaves your brand open to copying or to someone registering it first. We advise whether a Madrid Protocol application or a direct national filing suits {name}, and coordinate the application with local requirements in mind.",
            "We follow examination and oppositions abroad and pass on each development with a clear recommendation.",
        ],
        includes=[
            "Advice on Madrid Protocol versus national filing",
            "Availability search in the target country",
            "Application drafting and filing coordination",
            "Examination and objection follow-up",
            "Renewal tracking across countries",
        ],
    ),
    "Designs": dict(
        icon="bezier2", image="trademark",
        lede="Protect the shape, pattern and look of your product with {name}.",
        overview=[
            "Design registration protects how a product looks — its shape, configuration, pattern or ornamentation. We check novelty, prepare representations that meet the Design Office's requirements and file {name} under the right class.",
            "We track the application through examination and keep a record of renewal dates so protection runs its full term.",
        ],
        includes=[
            "Novelty and prior-design check",
            "Preparation of design representations",
            "Classification and application filing",
            "Examination follow-up",
            "Renewal tracking",
        ],
    ),
    "GI": dict(
        icon="geo-alt", image="trademark",
        lede="Protect products tied to a region's origin and reputation with {name}.",
        overview=[
            "Geographical Indications protect products whose quality or reputation comes from where they are made. {name} needs careful documentation of origin, production methods and the producer community, and we prepare that case thoroughly.",
            "We support producer associations through examination and help act against misuse of the GI after registration.",
        ],
        includes=[
            "Review of eligibility and origin documentation",
            "Statement of case preparation",
            "Filing with the GI Registry",
            "Examination and hearing support",
            "Post-registration enforcement guidance",
        ],
    ),
    "Advisory": dict(
        icon="clipboard-data", image="financial-reporting",
        lede="Understand what your intellectual property is worth and what risks it carries with {name}.",
        overview=[
            "Before an investment, acquisition or licensing deal, you need a clear view of the intellectual property involved. Our {name} reviews ownership, validity, encumbrances and commercial value, and sets out the findings in a report decision-makers can use.",
            "We flag issues early so they can be fixed or priced in before anything is signed.",
        ],
        includes=[
            "Scope definition with your team",
            "Verification of ownership and status",
            "Risk and validity review",
            "Valuation or findings report",
            "Recommendations and next steps",
        ],
    ),
    "TM Watch": dict(
        icon="eye", image="trademark",
        lede="Spot conflicting marks while there is still time to act, with {name}.",
        overview=[
            "New applications similar to your mark are published every week, and the window to oppose them is limited. With {name}, we review the Trade Marks Journal and registry data for conflicting marks and alert you while action is still possible.",
            "Each alert comes with our assessment of the risk and the options open to you.",
        ],
        includes=[
            "Watch set-up for your marks and classes",
            "Regular journal and registry review",
            "Conflict alerts with a risk assessment",
            "Opposition deadline tracking",
            "Periodic watch reports",
        ],
    ),
    "Copyright": dict(
        icon="file-earmark-richtext", image="trademark",
        lede="Secure your creative and software work with {name}.",
        overview=[
            "Copyright protects original literary, artistic, musical and software works, and registration gives you documented proof of ownership that makes enforcement far simpler. We handle {name}, preparing the work samples, statements and authorisations the Copyright Office asks for.",
            "We follow up on discrepancies and objections until the matter is closed.",
        ],
        includes=[
            "Assessment of the work and its ownership",
            "Preparation of forms and samples",
            "Filing with the Copyright Office",
            "Responses to discrepancies or objections",
            "Certificate and record handover",
        ],
    ),
    "Patent": dict(
        icon="lightbulb", image="trademark",
        lede="Protect your invention with {name}, from the first search to grant.",
        overview=[
            "A patent gives you exclusive rights over an invention, but only when novelty, inventive step and drafting are handled with care. We support {name} with technical searches, clear specifications and timely responses to the Patent Office.",
            "We track statutory deadlines for examination requests, responses and renewals throughout the patent's life.",
        ],
        includes=[
            "Prior-art search and patentability opinion",
            "Specification drafting support",
            "Filing and examination requests",
            "Responses to examination reports and hearings",
            "Deadline and renewal tracking",
        ],
    ),
    "Secretarial": dict(
        icon="journal-check", image="corporate-compliance",
        lede="Keep your company's ROC record clean, with {name} handled by our secretarial team.",
        overview=[
            "Company and LLP law requires timely filings and properly documented decisions, and missed forms quickly turn into penalties. We handle {name} — drafting resolutions, preparing forms and filing them on the MCA portal within the due dates.",
            "We keep a compliance calendar for your entity so recurring filings never slip.",
        ],
        includes=[
            "Review of applicable requirements",
            "Drafting of resolutions, minutes and notices",
            "Preparation and filing of MCA forms",
            "Follow-up on approvals and resubmissions",
            "Compliance calendar for recurring filings",
        ],
    ),
    "Tax Filing/Compliance": dict(
        icon="receipt", image="taxation-planning",
        lede="Accurate, on-time {name}, so you avoid notices, interest and penalties.",
        overview=[
            "Tax compliance is a recurring cycle of registrations, returns and reconciliations, each with its own due date. We handle {name} by reconciling your books against GST, TDS and income tax records, so what you file matches what the department sees.",
            "If a notice does arrive, we help you understand it and respond with the right documentation.",
        ],
        includes=[
            "Review of your records and applicable obligations",
            "Reconciliation with portal data",
            "Preparation and filing within due dates",
            "Acknowledgements and record keeping",
            "Support with notices and queries",
        ],
    ),
    "Accounting & CFO": dict(
        icon="calculator", image="virtual-accounting",
        lede="Reliable numbers and practical financial guidance with {name}.",
        overview=[
            "Good decisions depend on accurate, timely financial information. Our {name} gives you a structured process, clear reports and a team that understands both accounting standards and the realities of running a business.",
            "We work remotely with the tools you already use, so the engagement fits around how your business operates today.",
        ],
        includes=[
            "Understanding your business and reporting needs",
            "Defined scope, timelines and deliverables",
            "Work carried out by experienced professionals",
            "Clear reports with findings and recommendations",
            "Ongoing support and review meetings",
        ],
    ),
    "Contracts & Agreements": dict(
        icon="file-earmark-text", image="corporate-compliance",
        lede="{name} drafted around your arrangement, reviewed with you clause by clause and ready to execute.",
        overview=[
            "A well-drafted document prevents disputes by making each party's rights and obligations clear. We prepare your {name} around the specifics of your situation rather than a generic template, and explain each key clause in plain language.",
            "Where registration or stamp duty applies, we guide you through execution so the document is legally enforceable.",
        ],
        includes=[
            "Understanding of the arrangement and the parties",
            "Drafting tailored to your terms",
            "Review and revision rounds",
            "Stamp duty and registration guidance",
            "Final, execution-ready document",
        ],
    ),
    "Legal Services": dict(
        icon="briefcase", image="corporate-compliance",
        lede="{name}, handled by professionals who explain your options clearly and act on them promptly.",
        overview=[
            "Legal matters run on deadlines and procedure, and the first step often shapes the outcome. For {name}, we review your documents and facts, explain the options available and prepare what's needed to act.",
            "We keep you informed at each stage and coordinate with advocates where representation is required.",
        ],
        includes=[
            "Consultation and document review",
            "Assessment of options and likely next steps",
            "Drafting of notices, petitions or applications",
            "Filing and follow-up",
            "Coordination with advocates where needed",
        ],
    ),
    "Convert Your Business": dict(
        icon="arrow-repeat", image="corporate-compliance",
        lede="Change or upgrade your business structure with {name}, managed end to end.",
        overview=[
            "As a business grows, the structure it started with may stop fitting — for raising funds, limiting liability or meeting client expectations. We handle {name}, including approvals, filings and moving your registrations and licences across.",
            "We plan the sequence of steps so day-to-day operations continue without interruption.",
        ],
        includes=[
            "Eligibility review and step-by-step plan",
            "Board or partner approvals and consents",
            "Filing of forms with the authority",
            "Updating PAN, GST, bank and licence records",
            "Post-completion compliance checklist",
        ],
    ),
}

PROCESS = {
    "startup": [
        ("Consultation", "We understand your business and confirm exactly what applies to you."),
        ("Documents", "You share the documents on our checklist; we review and prepare the file."),
        ("Filing", "We file with the authority and handle every query that comes back."),
        ("Approval", "You receive the certificate or licence along with your next compliance steps."),
    ],
    "ip-trademark": [
        ("Search and assessment", "We check existing rights and tell you the risks before anything is filed."),
        ("Drafting and filing", "We prepare the application or reply and file it with the right office."),
        ("Follow-up", "We track examination, objections, oppositions and hearings for you."),
        ("Protection", "Once registered, we track renewals and watch for conflicting filings."),
    ],
    "compliance": [
        ("Requirement review", "We confirm what's due, by when, and what we need from you."),
        ("Data and documents", "You share your records; we reconcile and prepare everything."),
        ("Preparation and filing", "We prepare, review with you and file within the due date."),
        ("Ongoing support", "We keep a calendar of recurring obligations and answer queries as they arise."),
    ],
}

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

e = html.escape


def slugify(name):
    s = name.lower().replace("&", " and ").replace("’", "").replace("'", "").replace(".", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def group_key(category, group):
    return category["key"] + "-" + slugify(group)


def build_index():
    """Flat list of service dicts, with duplicate-slug protection."""
    services, seen = [], {}
    for cat in CATALOG:
        for group, names in cat["groups"]:
            if group not in GROUP_COPY:
                raise SystemExit("No GROUP_COPY entry for sub-group: " + group)
            for name in names:
                slug = slugify(name)
                if slug in seen:
                    raise SystemExit("Duplicate slug %r for %r and %r" % (slug, seen[slug], name))
                seen[slug] = name
                services.append(dict(name=name, slug=slug, category=cat, group=group))
    return services


def replace_between(text, marker, content, indent):
    pattern = re.compile(
        r"(?P<indent>[ \t]*)<!-- %s:start -->.*?<!-- %s:end -->" % (marker, marker), re.S
    )
    if not pattern.search(text):
        raise SystemExit("Marker %s not found" % marker)
    block = (
        indent + "<!-- %s:start -->\n" % marker
        + content
        + indent + "<!-- %s:end -->" % marker
    )
    return pattern.sub(lambda _m: block, text, count=1)


def indent_block(text, indent):
    return "".join(indent + line + "\n" if line else "\n" for line in text.split("\n"))


# --------------------------------------------------------------------------
# Shared fragments
# --------------------------------------------------------------------------

def services_menu(prefix, home):
    """One navbar dropdown per category. Desktop: sub-groups listed on the
    left, the hovered sub-group's services on the right. Mobile: each
    sub-group is an expandable row. prefix = path to site root; home = the
    page holding the #services section (no-JS fallback for the toggles)."""
    items = []
    for cat in CATALOG:
        rail, panes = [], []
        for i, (group, names) in enumerate(cat["groups"]):
            key = group_key(cat, group)
            active = i == 0
            rail.append(
                '<button class="mega-menu__tab%s" id="mega-tab-%s" type="button" role="tab" '
                'data-bs-toggle="tab" data-bs-target="#mega-%s" aria-controls="mega-%s" aria-selected="%s"%s>'
                '%s<i class="bi bi-chevron-right" aria-hidden="true"></i></button>'
                % (" active" if active else "", key, key, key,
                   "true" if active else "false", "" if active else ' tabindex="-1"', e(group))
            )
            cols = 3 if len(names) > 18 else 2 if len(names) > 9 else 1
            links = "\n".join(
                '      <li><a href="%sservices/%s.html">%s</a></li>' % (prefix, slugify(n), e(n))
                for n in names
            )
            panes.append(
                '<div class="tab-pane mega-menu__pane%s" id="mega-%s" role="tabpanel" aria-labelledby="mega-tab-%s" tabindex="0">\n'
                '  <details class="mega-menu__group">\n'
                '    <summary>%s</summary>\n'
                '    <ul class="mega-menu__links" style="--cols: %d">\n%s\n    </ul>\n'
                '  </details>\n'
                '</div>' % (" show active" if active else "", key, key, e(group), cols, links)
            )
        items.append(
            '<li class="nav-item dropdown site-nav__mega">\n'
            '  <a class="nav-link dropdown-toggle" href="%s#services" role="button" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">%s <i class="bi bi-chevron-down site-nav__caret" aria-hidden="true"></i></a>\n'
            '  <div class="dropdown-menu mega-menu">\n'
            '    <div class="mega-menu__rail" role="tablist" aria-label="%s services">\n'
            '%s'
            '    </div>\n'
            '    <div class="tab-content mega-menu__panes">\n'
            '%s'
            '    </div>\n'
            '  </div>\n'
            '</li>'
            % (home, e(cat["name"]), e(cat["name"]),
               indent_block("\n".join(rail), "      "),
               indent_block("\n".join(panes), "      "))
        )
    return "\n".join(items)


def footer_services(prefix):
    return "\n".join(
        '<li><a href="%sservices/%s.html">%s</a></li>' % (prefix, slugify(n), e(n))
        for n in FOOTER_SERVICES
    )


def services_directory():
    """Homepage #services section: one tab per category, a card per sub-group."""
    VISIBLE = 6
    tabs, panes = [], []
    for i, cat in enumerate(CATALOG):
        active = i == 0
        count = sum(len(n) for _, n in cat["groups"])
        tabs.append(
            '<button class="services-tabs__tab%s" id="services-tab-%s" type="button" role="tab" '
            'data-bs-toggle="tab" data-bs-target="#services-%s" aria-controls="services-%s" aria-selected="%s"%s>'
            '<i class="bi bi-%s" aria-hidden="true"></i>%s <span class="services-tabs__count">%d</span></button>'
            % (" active" if active else "", cat["key"], cat["key"], cat["key"],
               "true" if active else "false", "" if active else ' tabindex="-1"',
               cat["icon"], e(cat["name"]), count)
        )
        cards = []
        for group, names in cat["groups"]:
            copy = GROUP_COPY[group]

            def items(subset, indent):
                return "\n".join(
                    '%s<li><a href="services/%s.html">%s</a></li>' % (indent, slugify(n), e(n))
                    for n in subset
                )

            more = ""
            if len(names) > VISIBLE:
                more = (
                    '\n    <details class="svc-group__more">\n'
                    '      <summary><span class="svc-group__more-open">Show %d more</span>'
                    '<span class="svc-group__more-close">Show fewer</span></summary>\n'
                    '      <ul class="svc-group__list">\n%s\n      </ul>\n'
                    '    </details>' % (len(names) - VISIBLE, items(names[VISIBLE:], "        "))
                )
            cards.append(
                '<div class="col">\n'
                '  <article class="svc-group">\n'
                '    <div class="svc-group__head">\n'
                '      <div class="icon-badge"><i class="bi bi-%s" aria-hidden="true"></i></div>\n'
                '      <div>\n'
                '        <h3>%s</h3>\n'
                '        <p class="svc-group__count">%d %s</p>\n'
                '      </div>\n'
                '    </div>\n'
                '    <ul class="svc-group__list">\n%s\n    </ul>%s\n'
                '  </article>\n'
                '</div>'
                % (copy["icon"], e(group), len(names), "service" if len(names) == 1 else "services",
                   items(names[:VISIBLE], "      "), more)
            )
        panes.append(
            '<div class="tab-pane fade%s" id="services-%s" role="tabpanel" aria-labelledby="services-tab-%s" tabindex="0">\n'
            '  <p class="services-tabs__blurb">%s</p>\n'
            '  <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">\n'
            '%s'
            '  </div>\n'
            '</div>'
            % (" show active" if active else "", cat["key"], cat["key"], e(cat["blurb"]),
               indent_block("\n".join(cards), "    "))
        )

    return (
        '<section id="services" class="section services">\n'
        '  <div class="container-custom">\n'
        '    <p class="pill-badge">Our Services</p>\n'
        '    <h2>Comprehensive Business Solutions</h2>\n'
        '    <p class="section-subtitle">\n'
        '      <strong>We bring every service your business needs under one roof.</strong>\n'
        '      From registration and licensing to IP protection and ongoing compliance,\n'
        '      pick a category to see everything we handle.\n'
        '    </p>\n'
        '\n'
        '    <div class="services-tabs" role="tablist" aria-label="Service categories">\n'
        '%s'
        '    </div>\n'
        '\n'
        '    <div class="tab-content">\n'
        '%s'
        '    </div>\n'
        '  </div>\n'
        '</section>'
        % (indent_block("\n".join(tabs), "      "), indent_block("\n".join(panes), "      "))
    )


# --------------------------------------------------------------------------
# Service page template
# --------------------------------------------------------------------------

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script>
    document.documentElement.classList.add("js");
  </script>
  <title>{title}</title>
  <meta name="description" content="{description}">

  <!-- Placeholder — replace with the live production domain before launch -->
  <link rel="canonical" href="{url}">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{site}assets/images/services/{image}.webp">
  <meta property="og:url" content="{url}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{site}assets/images/services/{image}.webp">

  <link rel="icon" type="image/png" sizes="32x32" href="../assets/images/favicon-32.png">
  <link rel="icon" type="image/png" sizes="512x512" href="../assets/images/favicon.png">
  <link rel="apple-touch-icon" sizes="180x180" href="../assets/images/apple-touch-icon.png">

  <script type="application/ld+json">
  {jsonld}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    rel="preload"
    as="style"
    href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap">
  <link
    href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap"
    rel="stylesheet"
    media="print"
    onload="this.media='all'">
  <noscript>
    <link
      href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap"
      rel="stylesheet">
  </noscript>

  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    rel="stylesheet"
    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
    crossorigin="anonymous">

  <link
    rel="preload"
    as="style"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
    rel="stylesheet"
    media="print"
    onload="this.media='all'">
  <noscript>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
      rel="stylesheet">
  </noscript>

  <link href="../css/style.css" rel="stylesheet">
</head>
<body>
  <!-- Generated by tools/build_services.py — edit the generator, not this file. -->

  <div id="preloader" class="preloader" aria-hidden="true">
    <img src="../assets/images/hasten_logo.png" alt="" class="preloader__logo">
  </div>
  <noscript>
    <style>#preloader {{ display: none !important; }}</style>
  </noscript>

  <a class="skip-link" href="#main">Skip to main content</a>

  <header>
    <nav class="navbar navbar-expand-xl site-nav fixed-top" id="siteNav" aria-label="Primary">
      <div class="container-custom">
        <a class="navbar-brand site-nav__brand" href="../index.html">
          <img src="../assets/images/hasten_logo.png" alt="Hasten Business Solutions LLP" class="site-nav__logo">
        </a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#siteNavCollapse"
          aria-controls="siteNavCollapse"
          aria-expanded="false"
          aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="siteNavCollapse">
          <ul class="navbar-nav site-nav__links">
            <li class="nav-item"><a class="nav-link" href="../index.html#home" data-nav-link>Home</a></li>
            <li class="nav-item"><a class="nav-link" href="../about.html" data-nav-link>About</a></li>
{menu}
            <li class="nav-item"><a class="nav-link" href="../index.html#testimonials" data-nav-link>Testimonials</a></li>
            <li class="nav-item"><a class="nav-link" href="../contact.html" data-nav-link>Contact</a></li>
          </ul>
          <a href="#enquire" class="btn btn-primary site-nav__cta d-xl-none" data-nav-link><span class="btn__label">Get Consultation</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></a>
        </div>
        <a href="#enquire" class="btn btn-primary site-nav__cta d-none d-xl-inline-flex" data-nav-link><span class="btn__label">Get Consultation</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></a>
      </div>
    </nav>
  </header>

  <main id="main" tabindex="-1">
    <section class="page-header service-hero">
      <div class="container-custom">
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <nav aria-label="Breadcrumb">
              <ol class="service-hero__crumbs">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../index.html#services">Services</a></li>
                <li>{category}</li>
                <li aria-current="page">{group}</li>
              </ol>
            </nav>
            <h1>{name}</h1>
            <p class="page-header__lede">{lede}</p>
            <div class="service-hero__actions">
              <a href="#enquire" class="btn btn-primary"><span class="btn__label">Get Started</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></a>
              <a href="https://wa.me/918078802553?text={wa_text}" class="btn btn-outline-light" target="_blank" rel="noopener noreferrer"><span class="btn__label">Ask on WhatsApp</span><span class="btn__icon"><i class="bi bi-whatsapp" aria-hidden="true"></i></span></a>
            </div>
          </div>
          <div class="col-lg-5 d-none d-lg-block">
            <div class="service-hero__media">
              <img src="../assets/images/services/{image}.webp" alt="{image_alt}" width="1000" height="625">
              <div class="service-hero__badge">
                <span class="icon-badge"><i class="bi bi-{icon}" aria-hidden="true"></i></span>
                <span>{group}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--light service-detail">
      <div class="container-custom">
        <div class="row g-5">
          <div class="col-lg-7">
            <p class="pill-badge">Overview</p>
            <h2>About {name}</h2>
{overview}
            <h3 class="service-detail__subheading">What's included</h3>
            <ul class="service-detail__list">
{includes}
            </ul>
          </div>

          <div class="col-lg-5">
            <div class="contact-form-panel service-detail__form" id="enquire">
              <h2 class="service-detail__form-title">Enquire about this service</h2>
              <p class="service-detail__form-lede">Share a few details and our team will get back to you.</p>
              <form id="contactForm" class="contact-form" novalidate>
                <input type="hidden" name="service" value="{name}">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label" for="fullName">Full Name <span class="text-danger" aria-hidden="true">*</span></label>
                    <input type="text" class="form-control" id="fullName" name="fullName" autocomplete="name" required>
                    <div class="invalid-feedback">Please enter your full name.</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="email">Email Address <span class="text-danger" aria-hidden="true">*</span></label>
                    <input type="email" class="form-control" id="email" name="email" autocomplete="email" required>
                    <div class="invalid-feedback">Please enter a valid email address.</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="phone">Phone Number</label>
                    <input type="tel" class="form-control" id="phone" name="phone" autocomplete="tel">
                  </div>
                  <div class="col-12">
                    <label class="form-label" for="message">Message <span class="text-danger" aria-hidden="true">*</span></label>
                    <textarea class="form-control" id="message" name="message" rows="3" required></textarea>
                    <div class="invalid-feedback">Please enter a message.</div>
                  </div>
                  <div class="col-12">
                    <button type="submit" class="btn btn-primary w-100"><span class="btn__label">Send Enquiry</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></button>
                  </div>
                </div>
              </form>

              <div class="contact-form__success" hidden tabindex="-1">
                <div class="icon-badge contact-form__success-icon"><i class="bi bi-check-lg" aria-hidden="true"></i></div>
                <h3>Thanks for reaching out.</h3>
                <p>Your enquiry about {name} has been received. Our team will get back to you shortly.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--dark service-process">
      <div class="container-custom">
        <p class="pill-badge pill-badge--on-dark">How it works</p>
        <h2>From first call to completion</h2>
        <ol class="row g-4 g-lg-5 service-process__steps">
{process}
        </ol>
      </div>
    </section>

    <section class="section service-related">
      <div class="container-custom">
        <p class="pill-badge">{group}</p>
        <h2>Related services</h2>
        <ul class="service-related__list">
{related}
        </ul>
      </div>
    </section>

    <section class="section section--dark cta">
      <img src="../assets/images/cta/team-meeting.webp" alt="" class="cta__bg" loading="lazy" aria-hidden="true">
      <div class="cta__overlay" aria-hidden="true"></div>
      <div class="cta__glow" aria-hidden="true"></div>
      <div class="container-custom cta__content">
        <h2>Let's Build a Stronger Business Together.</h2>
        <p class="section-subtitle">
          Whether you need accounting support, tax assistance, compliance
          services or digital growth solutions, Hasten is ready to help.
        </p>
        <div class="cta__actions">
          <a href="#enquire" class="btn btn-primary"><span class="btn__label">Talk to Our Team</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></a>
          <a href="../index.html#services" class="btn btn-outline-light"><span class="btn__label">Explore Services</span><span class="btn__icon"><i class="bi bi-arrow-up-right" aria-hidden="true"></i></span></a>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container-custom">
      <div class="row g-4 site-footer__top">
        <div class="col-12 col-lg-4">
          <a href="../index.html" class="site-footer__brand">
            <img src="../assets/images/hasten_logo.png" alt="Hasten Business Solutions LLP" class="site-footer__logo" loading="lazy">
          </a>
          <p class="site-footer__blurb">
            Professional business solutions designed to simplify, strengthen
            and support your business.
          </p>
          <div class="site-footer__social">
            <a href="https://www.facebook.com/hastenbs/" target="_blank" rel="noopener noreferrer" class="site-footer__social-link" aria-label="Hasten Business Solutions on Facebook">
              <i class="bi bi-facebook" aria-hidden="true"></i>
            </a>
            <a href="https://www.instagram.com/hastenbs/" target="_blank" rel="noopener noreferrer" class="site-footer__social-link" aria-label="Hasten Business Solutions on Instagram">
              <i class="bi bi-instagram" aria-hidden="true"></i>
            </a>
            <a href="https://in.linkedin.com/company/hastenbiz" target="_blank" rel="noopener noreferrer" class="site-footer__social-link" aria-label="Hasten Business Solutions on LinkedIn">
              <i class="bi bi-linkedin" aria-hidden="true"></i>
            </a>
          </div>
        </div>

        <div class="col-6 col-lg-2">
          <h3 class="site-footer__heading">Company</h3>
          <ul class="site-footer__links">
            <li><a href="../about.html">About</a></li>
            <li><a href="../index.html#services">Services</a></li>
            <li><a href="../index.html#why-us">Why Us</a></li>
            <li><a href="../index.html#testimonials">Testimonials</a></li>
            <li><a href="../contact.html">Contact</a></li>
          </ul>
        </div>

        <div class="col-6 col-lg-3">
          <h3 class="site-footer__heading">Services</h3>
          <ul class="site-footer__links">
{footer_services}
          </ul>
        </div>

        <div class="col-12 col-lg-3">
          <h3 class="site-footer__heading">Contact</h3>
          <ul class="site-footer__links">
            <li>KM SQUARE PALACHUVAD, 27/1901, Ambadimoola Rd, Thrikkakara, Vazhakkala, Kochi, Kakkanad, Kerala 682030</li>
            <li><a href="tel:+918078802553">080788 02553</a></li>
            <li><a href="https://wa.me/918078802553" target="_blank" rel="noopener noreferrer">WhatsApp: 080788 02553</a></li>
            <li><a href="mailto:hastenbs@gmail.com">hastenbs@gmail.com</a></li>
          </ul>
        </div>
      </div>

      <div class="site-footer__bottom">
        <p class="site-footer__copyright">
          &copy; <span id="copyrightYear"></span> Hasten Business Solutions LLP. All Rights Reserved.
        </p>
        <p class="site-footer__credit">
          Designed &amp; Developed by
          <a href="https://www.tinqbit.com/" target="_blank" rel="noopener noreferrer">Tinqbit Pvt Ltd</a>
        </p>
      </div>
    </div>
  </footer>

  <script
    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
    integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
    crossorigin="anonymous"></script>
  <script src="../js/script.js"></script>
</body>
</html>
"""


def render_service(svc, menu_html, footer_html):
    import json
    from urllib.parse import quote

    cat, group, name = svc["category"], svc["group"], svc["name"]
    copy = GROUP_COPY[group]
    fill = lambda t: t.format(name=name)
    lede = fill(copy["lede"])
    url = SITE_URL + "services/%s.html" % svc["slug"]

    siblings = next(n for g, n in cat["groups"] if g == group)
    related = [n for n in siblings if n != name][:12]
    if not related:
        related = [n for g, ns in cat["groups"] if g != group for n in ns][:8]

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "serviceType": group,
        "description": lede,
        "url": url,
        "areaServed": "IN",
        "provider": {
            "@type": "LocalBusiness",
            "name": "Hasten Business Solutions LLP",
            "telephone": "+918078802553",
            "email": "hastenbs@gmail.com",
        },
    }, indent=2, ensure_ascii=False).replace("\n", "\n  ")

    return PAGE.format(
        title=e("%s | Hasten Business Solutions LLP" % name),
        description=e(lede),
        url=url,
        site=SITE_URL,
        jsonld=jsonld,
        menu=indent_block(menu_html, "            ").rstrip("\n"),
        category=e(cat["name"]),
        group=e(group),
        name=e(name),
        lede=e(lede),
        wa_text=quote("Hi, I'd like to know more about %s." % name),
        image=copy["image"],
        image_alt=e(IMAGES[copy["image"]]),
        icon=copy["icon"],
        overview="\n".join(
            '            <p class="section-subtitle">%s</p>' % e(fill(p)) for p in copy["overview"]
        ),
        includes="\n".join(
            '              <li>%s</li>' % e(item) for item in copy["includes"]
        ),
        process="\n".join(
            '          <li class="col-sm-6 col-lg-3">\n'
            '            <div class="why-us__item">\n'
            '              <span class="index-marker">%02d</span>\n'
            '              <h3>%s</h3>\n'
            '              <p>%s</p>\n'
            '            </div>\n'
            '          </li>' % (i + 1, e(t), e(d))
            for i, (t, d) in enumerate(PROCESS[cat["key"]])
        ),
        related="\n".join(
            '          <li><a href="%s.html">%s <i class="bi bi-arrow-right" aria-hidden="true"></i></a></li>'
            % (slugify(n), e(n)) for n in related
        ),
        footer_services=indent_block(footer_services("../"), "            ").rstrip("\n"),
    )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    services = build_index()
    SERVICES_DIR.mkdir(exist_ok=True)

    menu_for_pages = services_menu("../", "../index.html")
    footer_for_pages = footer_services("../")
    wanted = set()
    for svc in services:
        path = SERVICES_DIR / (svc["slug"] + ".html")
        path.write_text(render_service(svc, menu_for_pages, footer_for_pages), encoding="utf-8")
        wanted.add(path.name)

    for stale in SERVICES_DIR.glob("*.html"):
        if stale.name not in wanted:
            stale.unlink()
            print("removed", stale.relative_to(ROOT))

    for page, home in (("index.html", ""), ("about.html", "index.html"), ("contact.html", "index.html")):
        path = ROOT / page
        text = path.read_text(encoding="utf-8")
        text = replace_between(text, "services-menu",
                               indent_block(services_menu("", home), "            "), "            ")
        text = replace_between(text, "footer-services",
                               indent_block(footer_services(""), "            "), "            ")
        if page == "index.html":
            text = replace_between(text, "services-directory",
                                   indent_block(services_directory(), "    "), "    ")
        path.write_text(text, encoding="utf-8")

    print("%d service pages written to %s/" % (len(services), SERVICES_DIR.relative_to(ROOT)))
    for cat in CATALOG:
        print("  %-15s %d" % (cat["name"], sum(len(n) for _, n in cat["groups"])))


if __name__ == "__main__":
    main()
