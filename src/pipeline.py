"""Retail portfolio project. Raw UCI XLSX or compatible CSV to audited SQLite and aggregates."""
import argparse, csv, json, sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
HEADERS=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
def records(path):
    if path.suffix.lower()=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f): yield row
    elif path.suffix.lower()=='.xlsx':
        try: import python_calamine
        except ImportError: raise SystemExit('For XLSX support: pip install python-calamine (or export Excel file as CSV)')
        book=python_calamine.CalamineWorkbook.from_path(str(path))
        sheet=book.get_sheet_by_index(0)
        rows=iter(sheet.to_python()); header=[str(x) for x in next(rows)]
        for cells in rows: yield dict(zip(header,cells))
    else: raise SystemExit('Input must be CSV or XLSX')

def dateparse(value):
    if isinstance(value,datetime): return value.strftime('%Y-%m-%d %H:%M:%S')
    txt=str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S','%Y-%m-%d %H:%M','%m/%d/%Y %H:%M','%Y-%m-%dT%H:%M:%S'):
        try: return datetime.strptime(txt,fmt).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError: pass
    return None

def csvout(path, rows, headers):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)

def build(path,out):
    out.mkdir(exist_ok=True,parents=True)
    db=out/'retail_analysis.sqlite';db.unlink(missing_ok=True)
    con=sqlite3.connect(db)
    con.executescript('''CREATE TABLE lines(invoice TEXT, stock TEXT, description TEXT, quantity INTEGER, timestamp TEXT, unit_price REAL, customer TEXT, country TEXT, revenue REAL); CREATE INDEX invoice_idx ON lines(invoice); CREATE INDEX customer_idx ON lines(customer); CREATE INDEX date_idx ON lines(timestamp);''')
    total=0; counts=defaultdict(int);batch=[];dates=[]
    for r in records(path):
        total+=1
        try:
            invoice=str(r['InvoiceNo']).strip();stock=str(r['StockCode']).strip()
            q=int(float(r['Quantity']));price=float(r['UnitPrice']);date=dateparse(r['InvoiceDate'])
        except (ValueError,TypeError,KeyError):counts['invalid_fields']+=1;continue
        if not date: counts['invalid_date']+=1;continue
        if invoice.upper().startswith('C') or q<=0:counts['cancellations_or_nonpositive_quantity']+=1;continue
        if price<=0:counts['nonpositive_price']+=1;continue
        customer=str(r.get('CustomerID') or '').strip()
        if customer.endswith('.0'): customer=customer[:-2]
        if not customer or customer.lower() in ('nan','none'):counts['missing_customer_id']+=1
        country=str(r.get('Country') or '').strip()
        batch.append((invoice,stock,str(r.get('Description') or '').strip(),q,date,price,customer,country,round(q*price,4)))
        if len(batch)>=10000:con.executemany('INSERT INTO lines VALUES(?,?,?,?,?,?,?,?,?)',batch);batch=[]
    if batch:con.executemany('INSERT INTO lines VALUES(?,?,?,?,?,?,?,?,?)',batch)
    con.commit()
    # A transaction = distinct (invoice,country) where invoice is sale; exclude empty customer only in retention metrics.
    kpis=con.execute('''SELECT ROUND(SUM(revenue),2),COUNT(DISTINCT invoice),COUNT(DISTINCT CASE WHEN customer<>'' THEN customer END),SUM(quantity),COUNT(*) FROM lines''').fetchone()
    metrics={'source':path.name,'source_rows':total,'included_line_items':kpis[4],'excluded':dict(counts),'sales_gbp':kpis[0],'orders':kpis[1],'identified_customers':kpis[2],'units':kpis[3], 'average_order_value_gbp':round(kpis[0]/kpis[1],2) if kpis[1] else None,'currency':'GBP','note':'Gross positive sales only; cancellations and returns excluded. Not net revenue, profitability, true conversion rate or marketing ROI.'}
    (out/'kpis.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    queries={
      'monthly_sales':('SELECT SUBSTR(timestamp,1,7) month, ROUND(SUM(revenue),2) sales_gbp,COUNT(DISTINCT invoice) orders FROM lines GROUP BY 1 ORDER BY 1',['month','sales_gbp','orders']),
      'country_sales':('SELECT country,ROUND(SUM(revenue),2) sales_gbp,COUNT(DISTINCT invoice) orders FROM lines GROUP BY 1 ORDER BY 2 DESC',['country','sales_gbp','orders']),
      'top_products':('SELECT stock,MAX(description) product,ROUND(SUM(revenue),2) sales_gbp,SUM(quantity) units FROM lines GROUP BY stock ORDER BY 3 DESC LIMIT 20',['stock','product','sales_gbp','units']),
      'customer_rfm':('''WITH orders AS (SELECT customer,invoice,MIN(timestamp) ts,SUM(revenue) amount FROM lines WHERE customer<>'' GROUP BY customer,invoice), latest AS (SELECT MAX(DATE(ts)) as max_date FROM orders) SELECT customer,CAST(julianday((SELECT max_date FROM latest))-julianday(MAX(DATE(ts))) AS INTEGER) recency_days,COUNT(*) frequency,ROUND(SUM(amount),2) monetary_gbp FROM orders GROUP BY customer ORDER BY monetary_gbp DESC''',['customer','recency_days','frequency','monetary_gbp']),
      'cohort_repeat':('''WITH orders AS (SELECT customer,invoice,MIN(timestamp) ts FROM lines WHERE customer<>'' GROUP BY customer,invoice), firsts AS (SELECT customer,MIN(SUBSTR(ts,1,7)) cohort FROM orders GROUP BY customer), customers AS (SELECT firsts.cohort,orders.customer, COUNT(*) n FROM orders JOIN firsts USING(customer) GROUP BY 1,2) SELECT cohort,COUNT(*) customers, SUM(CASE WHEN n>1 THEN 1 ELSE 0 END) repeat_customers,ROUND(100.0*SUM(CASE WHEN n>1 THEN 1 ELSE 0 END)/COUNT(*),2) repeat_pct FROM customers GROUP BY cohort ORDER BY cohort''',['cohort','customers','repeat_customers','repeat_pct'])
    }
    for name,(query,headers) in queries.items():csvout(out/(name+'.csv'),con.execute(query).fetchall(),headers)
    con.close();print(json.dumps(metrics,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',type=Path,default=BASE/'outputs');a=p.parse_args();build(a.input,a.output)
