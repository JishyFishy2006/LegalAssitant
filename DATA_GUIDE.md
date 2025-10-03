# Guide to Sourcing and Adding Data for the Legal Voice RAG MVP

This guide provides a central place for all instructions on what data to find, what format it needs to be in, and how to add it to this project.

---

## How to "Upload" Data

"Uploading" data to this project simply means **placing the correct files into the correct local directories** within the `data/` folder. Once the files are in place, the project's scripts will handle the rest.

---

## Step 1: Find Your Source Documents

The system is designed to ingest three types of documents: PDFs, HTML files, and JSON data. Here’s what to look for:

### **PDF Documents**
*   **What to look for**: Government regulations, legal acts, policy documents, and official notices. Good sources are agencies like the HHS, CMS, and CFPB.
*   **Required Format**:
    *   Must be **text-based**, not scanned images. You should be able to select and copy text from the PDF.
    *   Should have a clear, structured format with headings and sections for effective parsing.
*   **Example**: The [No Surprises Act Interim Final Rule](https://www.cms.gov/files/document/no-surprises-act-interim-final-rule.pdf) is a perfect example.

### **HTML Content**
*   **What to look for**: Web pages from government or legal resource websites that contain guidance, rules, or consumer information.
*   **Required Format**:
    *   Save the full HTML of the page.
    *   The page must have clear headings (`<h1>`, `<h2>`, etc.) to define sections.
    *   The content should be substantial (ideally >500 words per section).
*   **Example**: A guidance page from the [Consumer Financial Protection Bureau (CFPB)](https://www.consumerfinance.gov/consumer-tools/).

### **JSON Data**
*   **What to look for**: Structured data from government APIs or open data portals.
*   **Required Format**:
    *   Well-formed JSON, typically an array of objects or an object containing a results array.
*   **Example**: Data from the [CFPB Consumer Complaint Database API](https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/).

---

## Step 2: Place Source Files in `data/sources/`

Once you have your source files, place them in the correct subdirectory:

1.  **PDFs** go into: `data/sources/pdf/`
2.  **HTML files** go into: `data/sources/html/`
3.  **JSON files** go into: `data/sources/json/`

**File Naming Convention**: Use a descriptive, unique name for each file, as this will be used as an identifier. For example: `no_surprises_act_2021.pdf`.

---

## Step 3: Create a Manifest File for Each Source

For **every source document** you add, you must create a corresponding JSON manifest file. This file tells the system about your data.

1.  **Create a new `.json` file** in the `data/sources/manifests/` directory.
2.  **Use the template below** to fill in the details for your source document.

### Manifest Template (`.json`):
```json
{
  "source_id": "unique_identifier_for_your_document",
  "title": "The full title of the document",
  "description": "A brief description of what the document contains",
  "type": "pdf",
  "url": "The original URL where you found the document",
  "date": "YYYY-MM-DD",
  "agency": "The agency that published it (e.g., HHS/CMS, CFPB)",
  "tags": ["relevant", "keywords", "for", "search"],
  "priority": "high"
}
```

### Field Explanations:
*   `source_id`: A unique ID. A good practice is to use the filename without the extension (e.g., `no_surprises_act_2021`).
*   `title`: The official title of the document.
*   `type`: The file format. Must be one of `pdf`, `html`, or `json`.
*   `url`: The source URL.
*   `date`: The publication date.
*   `agency`: The publishing government agency.
*   `tags`: A list of keywords.

---

## What Happens Next?

Once you have placed your source files and created their corresponding manifests, you are ready for the next phase. The `ingest_sources.py` script will use your manifests to find the source files, parse them, and create the normalized `records.jsonl` file, which is then used to build the search index.
