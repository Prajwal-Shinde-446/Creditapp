import json
from datetime import datetime

# Read the original JSON file
with open('loan_data.json', 'r') as file:
    data = json.load(file)

# Transform the data to match Django model field names
transformed_data = [
    {
        "model": "credit_app.loan",
        "pk": entry["Loan ID"],
        "fields": {
            "customer": entry["Customer ID"],
            "loan_id": entry["Loan ID"],
            "loan_amount": entry["Loan Amount"],
            "tenure": entry["Tenure"],
            "interest_rate": entry["Interest Rate"],
            "monthly_repayment": entry["Monthly payment"],
            "emis_paid_on_time": entry["EMIs paid on Time"],
            "start_date": datetime.utcfromtimestamp(entry["Date of Approval"] / 1000).strftime('%Y-%m-%d'),
            "end_date": datetime.utcfromtimestamp(entry["End Date"] / 1000).strftime('%Y-%m-%d'),
        }
    }
    for entry in data
]

# Write the transformed data back to the JSON file
with open('loan_data_transformed.json', 'w') as file:
    json.dump(transformed_data, file, indent=2)
