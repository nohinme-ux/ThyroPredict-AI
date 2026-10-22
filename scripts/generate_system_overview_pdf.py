import os
import sys
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "ThyroPredict AI — Comprehensive Project Overview & Feature Specification")
            self.drawRightString(612 - 54, 755, "Confidential Clinical Research Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 612 - 54, 747)
            
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        self.drawString(54, 36, "ThyroPredict AI v1.0.0 | Production: https://thyropredict-ai.vercel.app")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()

def build_pdf(filename="ThyroPredict_AI_Project_Overview.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A") # Slate 900
    brand_blue = colors.HexColor("#0284C7")    # Sky 600
    accent_teal = colors.HexColor("#0D9488")   # Teal 600
    text_dark = colors.HexColor("#1E293B")     # Slate 800
    muted_text = colors.HexColor("#475569")    # Slate 600
    bg_light = colors.HexColor("#F8FAFC")      # Slate 50
    border_color = colors.HexColor("#E2E8F0")  # Slate 200

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=brand_blue,
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=muted_text
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=brand_blue,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0369A1")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=text_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=primary_color
    )

    story = []

    # --- TITLE / COVER HEADER ---
    story.append(Paragraph("ThyroPredict AI", title_style))
    story.append(Paragraph("Comprehensive Project Overview, Technical Architecture & Clinical Features", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=brand_blue, spaceAfter=10))

    meta_text = (
        "<b>Production URL:</b> <font color='#0284c7'><u>https://thyropredict-ai.vercel.app</u></font> &nbsp;|&nbsp; "
        "<b>Version:</b> 1.0.0 Production Release &nbsp;|&nbsp; "
        "<b>Date:</b> October 2026<br/>"
        "<b>Repository:</b> <font color='#0284c7'><u>https://github.com/nohinme-ux/ThyroPredict-AI.git</u></font> &nbsp;|&nbsp; "
        "<b>Lead Researcher Account:</b> researcher@thyropredict.ai"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 14))

    # Callout Banner
    callout_data = [[
        Paragraph("<b>Clinical Classification:</b> Explainable AI (XAI) Clinical Decision Support System (CDSS) for Thyroid Spectrum Disorders. Designed for clinical audit, endocrinological research, and reproducible biostatistical modeling.", callout_style)
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F9FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 14))

    # --- 1. EXECUTIVE SUMMARY & CLINICAL RATIONALE ---
    story.append(Paragraph("1. Executive Summary & Clinical Rationale", h1_style))
    story.append(Paragraph(
        "Thyroid disorders—predominantly autoimmune Hashimoto's thyroiditis, primary hypothyroidism, and thyrotoxicosis—represent "
        "some of the most prevalent endocrine dysfunctions worldwide. While routine blood tests evaluate serum levels of Thyroid Stimulating "
        "Hormone (TSH) and Free Thyroxine (FT4), accurate differential diagnosis often requires complex multi-parametric synthesis across "
        "autoantibodies (Anti-TPO), inflammatory cytokines (IL-6, Visfatin), lipid profiles, and metabolic comorbidities.",
        body_style
    ))
    story.append(Paragraph(
        "Modern deep learning architectures (e.g., deep neural networks, ensemble gradient boosters) frequently attain high benchmark accuracy "
        "but operate as opaque 'black boxes.' In clinical healthcare, an unexplainable diagnosis creates severe medico-legal liabilities and "
        "fails to gain physician trust. <b>ThyroPredict AI solves this dilemma</b> by engineering deterministic, white-box <b>Decision Tree classifiers</b>. "
        "Every diagnostic prediction is coupled with an exact, node-by-node pathophysiological explanation rule traversing verified biochemical thresholds.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # --- 2. HOW THE APPLICATION WORKS ---
    story.append(Paragraph("2. System Architecture & How It Works", h1_style))
    story.append(Paragraph(
        "The application is structured into four tightly integrated layers, deployed on a unified global serverless cloud topology:",
        body_style
    ))

    arch_items = [
        "<b>1. Clinical Biomarker Ingestion:</b> A responsive React 19 single-page interface collects 23 standardized clinical, hemodynamic, and biochemical biomarkers with client-side range validation.",
        "<b>2. Strict Pydantic Data Clamping:</b> The FastAPI backend validates physiological bounds (e.g., TSH between 0.0001 and 300.0 uIU/mL, Anti-TPO between 0.0 and 2000.0 IU/mL), neutralizing malformed payloads and injection attempts.",
        "<b>3. Dual-Runtime Decision Tree Traversal:</b> The system evaluates patient feature vectors against pre-trained decision tree graphs, outputting the predicted diagnostic class, calibrated confidence scores, and exact decision path rules.",
        "<b>4. Relational Persistence & Audit Trail:</b> Predictions are linked to anonymized participant profiles in a serverless relational database, immediately populating real-time analytics dashboards and longitudinal audit logs."
    ]
    for item in arch_items:
        story.append(Paragraph(f"• {item}", bullet_style))
    story.append(Spacer(1, 10))

    # Architecture Overview Table
    arch_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Component", table_header_style), Paragraph("Technology", table_header_style), Paragraph("Key Functional Responsibility", table_header_style)],
        [Paragraph("Client Frontend", table_cell_bold), Paragraph("Web Application SPA", table_cell_style), Paragraph("React 19, TypeScript, Vite", table_cell_style), Paragraph("Interactive forms, visualizer, audit drawers, KPI charts", table_cell_style)],
        [Paragraph("API Gateway", table_cell_bold), Paragraph("Serverless Endpoint", table_cell_style), Paragraph("FastAPI, Starlette, Vercel", table_cell_style), Paragraph("Sub-second REST routing, JWT middleware, CORS negotiation", table_cell_style)],
        [Paragraph("Machine Learning", table_cell_bold), Paragraph("Dual Decision Trees", table_cell_style), Paragraph("Scikit-learn, Native Graph", table_cell_style), Paragraph("Zero-dependency edge inference, deterministic rule extraction", table_cell_style)],
        [Paragraph("Data & Storage", table_cell_bold), Paragraph("Relational ORM", table_cell_style), Paragraph("SQLAlchemy 2.0, SQLite", table_cell_style), Paragraph("Participant records, prediction histories, consent tracking", table_cell_style)],
    ]
    arch_table = Table(arch_data, colWidths=[90, 105, 120, 189])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # --- 3. DUAL MACHINE LEARNING MODEL SPECIFICATIONS ---
    story.append(Paragraph("3. Dual Machine Learning Model Specifications", h1_style))
    story.append(Paragraph(
        "ThyroPredict AI incorporates two distinct models trained and audited on rigorous clinical study cohorts:",
        body_style
    ))

    # Models Comparison Table
    model_data = [
        [Paragraph("Specification", table_header_style), Paragraph("STS Clinical Model (Primary)", table_header_style), Paragraph("UCI Benchmark Model (Validation)", table_header_style)],
        [Paragraph("Dataset Source", table_cell_bold), Paragraph("STS Clinical Thyroid Study (269 patients)", table_cell_style), Paragraph("UCI Thyroid Disease Repository (972 patients)", table_cell_style)],
        [Paragraph("Biomarker Inputs", table_cell_bold), Paragraph("23 clinical, lipid, hormonal, & serology markers", table_cell_style), Paragraph("21 standardized clinical & demographic features", table_cell_style)],
        [Paragraph("Diagnostic Classes", table_cell_bold), Paragraph("Autoimmune Disease, Euthyroid, Hyperthyroid, Primary Hypothyroidism", table_cell_style), Paragraph("Negative (Euthyroid), Primary Hypothyroid, Compensated Hypothyroid", table_cell_style)],
        [Paragraph("Test Accuracy", table_cell_bold), Paragraph("<b>94.44%</b> (Balanced Accuracy: 94.87%)", table_cell_style), Paragraph("<b>99.07%</b> (Test Accuracy)", table_cell_style)],
        [Paragraph("Macro F1-Score", table_cell_bold), Paragraph("<b>91.98%</b> (CV Macro F1: 1.00 ± 0.00)", table_cell_style), Paragraph("<b>94.61%</b> (Macro F1-Score)", table_cell_style)],
        [Paragraph("Primary Discriminators", table_cell_bold), Paragraph("Anti-TPO (> 37.50), TSH (> 5.16), FT3 (<= 2.15)", table_cell_style), Paragraph("TSH (> 6.05), FTI (<= 64.50), TT4 (<= 59.00)", table_cell_style)],
    ]
    model_table = Table(model_data, colWidths=[120, 192, 192])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_blue),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 14))

    # --- 4. KEY FEATURES & FUNCTIONAL MODULES ---
    story.append(Paragraph("4. Key Application Features & Functions", h1_style))

    features_list = [
        ("Feature 1: Interactive Clinical Predictor (/predict)",
         "Empowers researchers to input multi-parametric clinical profiles. Includes a real-time model switch (STS vs. UCI), "
         "instant physiological sanity validation, and four one-click clinical scenario presets: Hashimoto's Autoimmune Disease, "
         "Overt Primary Hypothyroidism, Euthyroid Control, and Thyrotoxicosis."),
        
        ("Feature 2: Explainable AI Decision Rule Visualizer",
         "Deconstructs every diagnosis into transparent tree traversals. Clinicians can review the exact biomarker threshold "
         "that triggered the branch, inspecting the leaf purity, sample support, and multi-class probability breakdown."),
        
        ("Feature 3: Research Participant & Cohort Registry (/participants)",
         "Maintains longitudinal subject tracking with unique de-identified study codes (e.g., THYRO-PART-001). Tracks consent "
         "status, demographics, clinical notes, and maintains cascade referential integrity across prediction evaluations."),
        
        ("Feature 4: Real-Time Analytics & Cohort Overview Dashboard (/)",
         "Presents high-level research KPIs: total cohort enrollment, cumulative predictions executed, diagnosis prevalence "
         "pie/bar distributions, and a live stream of recent diagnostic transactions."),
        
        ("Feature 5: Longitudinal Prediction History & Audit Drawer (/history)",
         "A searchable, filterable audit registry. Researchers can search by patient code or diagnosis, open an audit drawer "
         "to inspect the original raw 23-biomarker payload, review previous decision rules, and export specific cases."),
        
        ("Feature 6: Dataset Insights & Exploratory Data Analysis (/dataset-insights)",
         "Visualizes the clinical distribution of the underlying training data, providing box plots, quartiles, and epidemiological "
         "breakdowns for TSH, FT3, FT4, and autoantibody titers across cohorts."),
        
        ("Feature 7: De-Identified Research Data Export (/api/research/export)",
         "Generates an RFC-4180 compliant CSV stream containing complete biomarker vectors, predicted outcomes, confidence scores, "
         "and decision path strings formatted for instant biostatistical analysis in R, SPSS, Stata, or Python."),
        
        ("Feature 8: Role-Based Authentication & Cryptographic Security",
         "Secures all clinical endpoints with cryptographic JWT tokens and salted bcrypt password hashing, ensuring that sensitive "
         "study data remains fully protected in multi-tenant environments.")
    ]

    for title, desc in features_list:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    # --- 5. COMPREHENSIVE REST API REFERENCE ---
    story.append(Paragraph("5. Complete REST API Reference Table", h1_style))

    api_data = [
        [Paragraph("Method", table_header_style), Paragraph("Endpoint Path", table_header_style), Paragraph("Auth Required", table_header_style), Paragraph("Description & Return Payloads", table_header_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/health", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Service health check and model loading status verification", table_cell_style)],
        [Paragraph("POST", table_cell_bold), Paragraph("/api/auth/login", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Authenticates email/password; returns JWT access token", table_cell_style)],
        [Paragraph("POST", table_cell_bold), Paragraph("/api/auth/register", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Registers a new clinical researcher user account", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/auth/me", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Retrieves profile information for the authenticated user", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/model/info", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Returns active model catalog, feature counts, and versions", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/model/metrics", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Returns accuracy, confusion matrices, and feature importances", table_cell_style)],
        [Paragraph("POST", table_cell_bold), Paragraph("/api/predictions", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Executes decision tree inference; returns class & rule paths", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/predictions", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Retrieves historical predictions log with filter parameters", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/predictions/{id}", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Retrieves detailed prediction record and raw feature payload", table_cell_style)],
        [Paragraph("DELETE", table_cell_bold), Paragraph("/api/predictions/{id}", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Permanently deletes an individual historical prediction record", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/participants", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Lists all enrolled research cohort participants", table_cell_style)],
        [Paragraph("POST", table_cell_bold), Paragraph("/api/participants", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Creates a new research participant with consent status", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/overview/stats", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Aggregates dashboard metrics, KPI counters, and breakdowns", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/dataset/summary", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Descriptive statistics and demographic summaries of datasets", table_cell_style)],
        [Paragraph("GET", table_cell_bold), Paragraph("/api/research/export", table_cell_style), Paragraph("Bearer Token", table_cell_style), Paragraph("Streams complete de-identified audit trail as an RFC-4180 CSV", table_cell_style)],
    ]

    api_table = Table(api_data, colWidths=[55, 135, 75, 239])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 14))

    # --- 6. REGULATORY & CLINICAL RESEARCH NOTICE ---
    story.append(Paragraph("6. Research Use & Regulatory Disclaimer", h1_style))
    disclaimer_text = (
        "<b>Notice of Research Use Only (RUO):</b> ThyroPredict AI is engineered solely as an academic and clinical research "
        "decision-support platform. It is not approved by the U.S. Food and Drug Administration (FDA), European Medicines Agency (EMA), "
        "or Central Drugs Standard Control Organisation (CDSCO) as an autonomous primary diagnostic device. Healthcare practitioners "
        "must integrate ThyroPredict AI predictions with independent laboratory serology, ultrasonography, clinical symptomatology, "
        "and medical history before instituting clinical management or pharmacotherapy."
    )
    disclaimer_data = [[Paragraph(disclaimer_text, callout_style)]]
    disclaimer_table = Table(disclaimer_data, colWidths=[504])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FECACA")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(disclaimer_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated: {filename}")

if __name__ == '__main__':
    target = os.path.join(r"c:\ThyroPredict AI", "ThyroPredict_AI_Project_Overview.pdf")
    build_pdf(target)
