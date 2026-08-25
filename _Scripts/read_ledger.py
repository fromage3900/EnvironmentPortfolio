import json

with open('C:/EnvironmentPortfolio/BS_GodFile/Saved/gate_ledger.json', 'r') as f:
    ledger = json.load(f)

print('Gate ledger:')
print('Total entries: ' + str(len(ledger['gates'])))
print()

# Group by status
status_counts = {}
for g in ledger['gates']:
    s = g['status']
    status_counts[s] = status_counts.get(s, 0) + 1
print('Status counts: ' + str(status_counts))
print()

# Show all gates
for g in ledger['gates']:
    note = g.get('note', '')[:80]
    print('  ' + g['id'] + ': ' + g['status'] + ' ' + g.get('date', '?') + ' - ' + note)