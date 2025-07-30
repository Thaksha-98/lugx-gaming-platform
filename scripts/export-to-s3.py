import boto3
import clickhouse_connect
import pandas as pd
from datetime import datetime

client = clickhouse_connect.get_client(host='clickhouse.lugx.svc.cluster.local', port=8123)

df = client.query_df('SELECT * FROM web_analytics')

s3 = boto3.client('s3', region_name='us-east-1')
csv_buffer = df.to_csv(index=False)
s3.put_object(Bucket='lugx-analytics-data-thaksha', Key=f'web_analytics_{datetime.now().isoformat()}.csv', Body=csv_buffer)
