# HR Resume AI Parser

Odoo 19 module that parses resumes (PDF), extracts text, runs AI-based structuring, normalizes skills, computes experience and match score, and detects duplicates/similar resumes.

## What it does

- **PDF extraction** – Extracts text from PDFs attached to applicants (via `pdfminer.six`).
- **AI parsing** – Produces structured data (skills, experience, education) from resume text (configurable AI provider).
- **Skill normalization** – Maps extracted skills to `hr.skill` with optional auto-creation.
- **Match score** – Computes a job match score per applicant.
- **Duplicates** – Flags possible duplicates by email/phone.
- **Similarity** – Detects similar resumes (cron + manual action).
- **Bulk upload** – Wizard to upload multiple PDFs and create one applicant per file.
- **AI Ranking** – List/dashboard of applicants ordered by match score and parsing confidence.

## Requirements

- **Odoo 19**
- **Python 3.10** (recommended; matches project `venv310`)
- **Python package:** `pdfminer.six` (provides the `pdfminer` module)

The module declares `pdfminer` as an external dependency; Odoo will warn if it is missing.

## Installation

### 1. Install Python dependency

Use the same Python that runs Odoo (e.g. project venv):

```bash
# Example: project venv310
/path/to/Odoo_19_ARMORA/venv310/bin/pip install "pdfminer.six==20220319"
```

Or install the full project requirements (includes `pdfminer.six` and all Odoo deps):

```bash
cd /path/to/Odoo_19_ARMORA
venv310/bin/pip install -r requirements.txt
```

### 2. Run Odoo with that environment

Start Odoo with the interpreter where `pdfminer` is installed so the module can load and parse PDFs:

```bash
cd /path/to/Odoo_19_ARMORA
./venv310/bin/python odoo-bin -c .openerp_serverrc
```

Or use the helper script (auto-installs `packaging` and `pdfminer.six` if missing):

```bash
./run_odoo.sh -c .openerp_serverrc
```

### 3. Install the module in Odoo

- Go to **Apps**, search for **HR Resume AI Parser**.
- Click **Install**.

If you see *“external dependency is not met: pdfminer”*, Odoo is not using the Python environment where `pdfminer.six` is installed. Use the same interpreter as in step 2 (e.g. `venv310/bin/python` or `run_odoo.sh`).

## What to do in Odoo

### Single applicant

1. **Recruitment → Applications** (or your Applications menu).
2. Create or open an applicant.
3. Attach a **PDF resume** to the applicant (drag & drop or Attachments).
4. The module will:
   - Extract text from the PDF.
   - Run AI parsing (if configured) and fill **Parsed Resume** tab: status, match score, confidence, extracted skills, parsed JSON.
5. Use **Parsed Resume** tab to see status, match score, confidence, duplicates, similar resumes, and “Compute similar resumes” if needed.

### Bulk upload

1. **Recruitment → Applications → Bulk Resume Upload**.
2. Select a **Job position**.
3. Upload one or more PDF files.
4. Confirm; the wizard creates one applicant per PDF and triggers parsing for each.

### AI Ranking

1. **Recruitment → Applications → AI Ranking**.
2. View applicants with parsed resumes, ordered by match score and confidence.
3. Use search/filters (Parsed, With job, High match, High confidence, Group by Job / Parsing status) as needed.

### Settings

- **Settings → General Settings** (or **Recruitment** settings, depending on where the option is placed): **Auto-create skills** – when enabled, unknown skills from parsing are created in `hr.skill`.

## Cron jobs

Two scheduled actions run in the background:

- **HR Resume Parser: Process Pending** – processes applicants in “pending” parsing state (interval: every 1 minute).
- **HR Resume Parser: Compute Similarities** – computes resume similarities (interval: every 6 hours).

You can adjust or disable them under **Settings → Technical → Automation → Scheduled Actions**.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| *“Package packaging is required to parse pdfminer.six…”* | Run Odoo with an environment where `packaging` is installed (e.g. `venv310` or `pip install packaging` in that env). |
| *“External dependency is not met: pdfminer”* | Install `pdfminer.six` in the same Python that runs Odoo: `pip install "pdfminer.six==20220319"`, then restart Odoo with that interpreter. |
| Parsing never runs / stays “Pending” | Ensure the cron “HR Resume Parser: Process Pending” is active and the server is running so jobs are executed. |
| No AI parsing / empty parsed data | The AI parsing step depends on your configured provider (see `resume_ai_parser_service`). Implement or configure the AI backend and ensure the cron or manual reprocess runs. |

## License

LGPL-3.

## Author

ARMORAIT.
