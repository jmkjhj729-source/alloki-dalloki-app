from __future__ import annotations
from pathlib import Path
import os

def upload_file_s3(local_path: Path, bucket: str, key: str, public_url_base: str = "", presign_seconds: int = 604800) -> str:
    """
    Upload to S3 and return URL.
    - If public_url_base provided: returns public_url_base + key
    - Else returns a presigned URL (7 days default) for private buckets.
    Requires AWS credentials in env/instance profile.
    """
    import boto3
    s3 = boto3.client("s3")
    s3.upload_file(str(local_path), bucket, key, ExtraArgs={"ContentType": "image/png"} if local_path.suffix.lower()==".png" else None)
    if public_url_base:
        base = public_url_base.rstrip("/") + "/"
        return base + key.lstrip("/")
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=int(presign_seconds),
    )

def upload_file_gdrive_service_account(local_path: Path, folder_id: str, sa_json_path: str) -> str:
    """
    Upload file to Google Drive using a service account.
    Returns a sharable file URL.
    NOTE: The Drive folder must be shared with the service account email.
    """
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(sa_json_path, scopes=scopes)
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": local_path.name, "parents": [folder_id]} if folder_id else {"name": local_path.name}
    media = MediaFileUpload(str(local_path), mimetype="image/png" if local_path.suffix.lower()==".png" else None, resumable=True)
    created = service.files().create(body=file_metadata, media_body=media, fields="id,webViewLink").execute()
    file_id = created["id"]

    # make anyone with link can view (optional but useful for direct delivery)
    try:
        service.permissions().create(fileId=file_id, body={"type":"anyone","role":"reader"}).execute()
    except Exception:
        pass

    # Prefer webViewLink; if missing, construct.
    return created.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"

def upload_bonus_assets(backend: str, local_paths: list[Path], require_stable_urls: bool=False, **kwargs) -> dict[str,str]:
    """
    Returns {filename: url}
    """
    out = {}
    if backend == "off":
        return out
    if backend == "s3":
        if require_stable_urls and not kwargs.get('public_url_base',''):
            raise ValueError('CloudFront/public base URL is required (S3_PUBLIC_URL_BASE) when require_stable_urls=True')
        bucket = kwargs.get("bucket","")
        prefix = kwargs.get("prefix","")
        public_base = kwargs.get("public_url_base","")
        presign = kwargs.get("presign_seconds", 604800)
        if not bucket:
            raise ValueError("S3 bucket is required for upload_backend=s3")
        for p in local_paths:
            key = (prefix.rstrip("/") + "/" + p.name).lstrip("/")
            out[p.name] = upload_file_s3(p, bucket=bucket, key=key, public_url_base=public_base, presign_seconds=presign)
        return out
    if backend == "gdrive":
        folder_id = kwargs.get("folder_id","")
        sa_json = kwargs.get("sa_json_path","")
        if not sa_json:
            raise ValueError("Service account json path is required for upload_backend=gdrive")
        for p in local_paths:
            out[p.name] = upload_file_gdrive_service_account(p, folder_id=folder_id, sa_json_path=sa_json)
        return out
    raise ValueError(f"Unknown backend: {backend}")


def upload_landing_html_s3(local_path: Path, bucket: str, key: str, public_url_base: str) -> str:
    """
    Upload landing.html to S3 and return stable CloudFront/public URL.
    Requires S3_PUBLIC_URL_BASE.
    """
    import boto3
    if not public_url_base:
        raise ValueError("S3_PUBLIC_URL_BASE is required for landing upload")
    s3 = boto3.client("s3")
    s3.upload_file(
        str(local_path),
        bucket,
        key,
        ExtraArgs={"ContentType": "text/html; charset=utf-8", "CacheControl": "max-age=60"}
    )
    base = public_url_base.rstrip("/") + "/"
    return base + key.lstrip("/")

def upload_landing_variants_s3(local_paths: list[Path], bucket: str, prefix: str, public_url_base: str) -> dict[str,str]:
    """
    Upload landing variants and return mapping {filename: stable_url}.
    """
    out = {}
    for p in local_paths:
        key = (prefix.rstrip("/") + "/" + p.name).lstrip("/")
        out[p.name] = upload_landing_html_s3(p, bucket=bucket, key=key, public_url_base=public_url_base)
    return out
