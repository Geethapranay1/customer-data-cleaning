import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def create_sample_customer_data(n_records=10000):
    
    np.random.seed(42)
    random.seed(42)
    
    customer_ids = [f"CUST_{i:06d}" for i in range(1, n_records + 1)]
    
    first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
    names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(n_records)]
    
    missing_indices = random.sample(range(n_records), int(n_records * 0.15))
    for idx in missing_indices:
        names[idx] = None
    
    emails = []
    for i in range(n_records):
        if random.random() < 0.1:  # 10% invalid emails
            emails.append(f"invalid_email_{i}")
        elif random.random() < 0.05:  # 5% missing
            emails.append(None)
        else:
            emails.append(f"user{i}@example.com")
    
    # Phone numbers with format inconsistencies
    phones = []
    for i in range(n_records):
        if random.random() < 0.08:  # 8% missing
            phones.append(None)
        else:
            base_phone = f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
            # Various formats
            formats = [
                base_phone,
                f"({base_phone[:3]}) {base_phone[3:6]}-{base_phone[6:]}",
                f"{base_phone[:3]}-{base_phone[3:6]}-{base_phone[6:]}",
                f"+1{base_phone}"
            ]
            phones.append(random.choice(formats))
    
    ages = np.random.normal(35, 12, n_records).astype(int)
    ages = np.clip(ages, 18, 80)
    outlier_indices = random.sample(range(n_records), 50)
    for idx in outlier_indices:
        ages[idx] = random.choice([5, 10, 150, 200])
    
    incomes = np.random.normal(55000, 20000, n_records)
    incomes = np.clip(incomes, 20000, 200000)
    # Add outliers
    for idx in random.sample(range(n_records), 100):
        incomes[idx] = random.choice([5000, 500000, 1000000])
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    reg_dates = []
    for _ in range(n_records):
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        formats = [
            random_date.strftime("%Y-%m-%d"),
            random_date.strftime("%m/%d/%Y"),
            random_date.strftime("%d-%m-%Y"),
            random_date.strftime("%B %d, %Y")
        ]
        reg_dates.append(random.choice(formats))
    
    statuses = []
    status_options = ['active', 'INACTIVE', 'Pending', 'suspended', 'Active']
    for _ in range(n_records):
        statuses.append(random.choice(status_options))
    
    # Create DataFrame
    df = pd.DataFrame({
        'CustomerID': customer_ids,
        'Name': names,
        'Email': emails,
        'Phone': phones,
        'Age': ages,
        'Income': incomes,
        'Registration_Date': reg_dates,
        'Status': statuses
    })
    
    
    duplicate_indices = random.sample(range(n_records), int(n_records * 0.08))
    duplicates = df.iloc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df


if __name__ == "__main__":
    df = create_sample_customer_data(10000)
    df.to_csv('data/raw_customer_data.csv', index=False)
    print(f"Sample dataset created with {len(df)} records")