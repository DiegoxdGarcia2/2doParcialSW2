#!/usr/bin/env python3
"""
Helper de Integración Real con Amazon S3 (servicio-de-seguros-aegiscore en us-east-2).
Permite a MS1 PHP 8.3 subir documentos RUAT/CI validados por IA Local (CU04),
certificados de póliza (CU02) y facturas PDF (CU05) usando las credenciales de .env.
"""

import base64
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.is_file():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)

    if len(sys.argv) >= 3:
        local_file_path = sys.argv[1]
        s3_key = sys.argv[2]
        content_type = sys.argv[3] if len(sys.argv) >= 4 else "application/pdf"
        base64_content = ""
    else:
        payload_file = Path(sys.argv[1])
        if not payload_file.is_file():
            print(json.dumps({"error": "Payload file not found"}))
            sys.exit(1)
        data = json.loads(payload_file.read_text(encoding="utf-8"))
        s3_key = data.get("s3_key", "documentos-polizas/doc.png")
        content_type = data.get("content_type", "image/png")
        local_file_path = data.get("local_file_path")
        base64_content = data.get("base64_content", "")

    bucket = os.environ.get("AWS_S3_BUCKET", "servicio-de-seguros-aegiscore")
    region = os.environ.get("AWS_S3_REGION", os.environ.get("AWS_REGION", "us-east-2"))
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if local_file_path and Path(local_file_path).is_file():
        raw_bytes = Path(local_file_path).read_bytes()
    else:
        if "," in base64_content:
            base64_content = base64_content.split(",", 1)[1]
        raw_bytes = base64.b64decode(base64_content)

    import boto3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=region,
    )
    filename = os.path.basename(s3_key)
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=raw_bytes,
        ContentType=content_type,
        ContentDisposition=f'inline; filename="{filename}"',
    )
    public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    print(
        json.dumps(
            {
                "uploaded": True,
                "status": "UPLOADED_TO_AWS_S3",
                "bucket": bucket,
                "region": region,
                "s3Key": s3_key,
                "s3_url": public_url,
                "s3Url": public_url,
                "sizeBytes": len(raw_bytes),
            }
        )
    )


if __name__ == "__main__":
    main()
