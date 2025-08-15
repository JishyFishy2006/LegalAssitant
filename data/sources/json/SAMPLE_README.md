# JSON Sources Directory

This directory should contain structured JSON data from government APIs and databases.

## Expected Sources:
- **CFPB Consumer Complaint Database** API responses
- **CMS Provider data** in JSON format
- **Government open data** JSON files
- **Legal database exports**

## Sample Files to Look For:
- Consumer complaint data from CFPB API
- Healthcare provider information
- Policy implementation data
- Regulatory compliance data

## File Structure Examples:

### Consumer Complaints (cfpb_complaints_sample.json):
```json
{
  "results": [
    {
      "complaint_id": "12345",
      "product": "Credit card",
      "issue": "Billing disputes",
      "company": "Example Bank",
      "state": "CA",
      "date_received": "2023-06-15",
      "consumer_complaint_narrative": "Detailed complaint text..."
    }
  ]
}
```

### Healthcare Data (cms_provider_sample.json):
```json
{
  "providers": [
    {
      "npi": "1234567890",
      "name": "Example Healthcare System",
      "specialty": "Internal Medicine",
      "location": "New York, NY",
      "billing_practices": "..."
    }
  ]
}
```

## File Naming:
- `cfpb_complaints_2023.json`
- `cms_provider_data.json`
- `healthcare_billing_data.json`
