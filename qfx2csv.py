import csv
from ofxparse import OfxParser

transaction_fields = ['total', 'income_type', 'unit_price', 'fees', 'type', 'commission', 'units', 'date', 'settleDate', 'amount']
fieldnames = ['date', 'type', 'security_type', 'ticker', 'unit_price', 'units', 'amount', 'total', 'commission', 'fees', 'income_type', 'name', 'settleDate']

def find_security(securities, id):
    for sec in securities:
        if sec.uniqueid == id:
            return sec

def main():
    with open('wealthfront.qfx', 'rb') as qfxfile:
        ofx = OfxParser.parse(qfxfile)

        rows = []
        for transaction in ofx.account.statement.transactions:
            row = {}

            public_props = (name for name in dir(transaction) if not name.startswith('_'))
            for field in transaction_fields:
                if field in dir(transaction):
                    row[field] = getattr(transaction, field)

            if 'security' in dir(transaction):
                security = find_security(ofx.security_list, transaction.security)
                row['ticker'] = security.ticker
                row['name'] = security.name

            if 'date' not in row:
                row['date'] = transaction.tradeDate

            if row['type'] == 'buymf':
                row['type'] = 'buy'
                row['security_type'] = 'fund'

            if row['type'] == 'sellmf':
                row['type'] = 'sell'
                row['security_type'] = 'fund'

            if row['type'] == 'buystock':
                row['type'] = 'buy'
                row['security_type'] = 'stock'

            if row['type'] == 'sellstock':
                row['type'] = 'sell'
                row['security_type'] = 'stock'

            rows.append(row)

    rows.sort(key=lambda row: row['date'])

    with open('result.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__== "__main__":
    main()
