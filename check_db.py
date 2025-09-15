import sqlite3

conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(f'  {table[0]}')

print()

# Check leads by organization
cursor.execute('SELECT organization_id, COUNT(*) FROM leads GROUP BY organization_id')
lead_counts = cursor.fetchall()
print('Leads by organization:')
for org_id, count in lead_counts:
    print(f'  Organization {org_id}: {count} leads')

print()

# Check contacts by organization  
cursor.execute('SELECT organization_id, COUNT(*) FROM contacts GROUP BY organization_id')
contact_counts = cursor.fetchall()
print('Contacts by organization:')
for org_id, count in contact_counts:
    print(f'  Organization {org_id}: {count} contacts')

conn.close()
