# upload to s3

import boto3

PDF_path = "./test123.pdf"
s3_bucket = "sym-public-assets"
s3_folder = "misc"
uuid = "test123"
s3_key = f'{s3_folder}/{uuid}.pdf'


s3 = boto3.client('s3')
s3.upload_file(
    PDF_path, 
    s3_bucket, 
    s3_key, 
    ExtraArgs={'ContentType': 'application/pdf'})
    

pdf_url = f"https://{s3_bucket}.s3.us-west-2.amazonaws.com/{s3_key}"

print(f"PDF uploaded to: {pdf_url}")