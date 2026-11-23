"""
Unit & Integration tests for Reports (CSV, Excel, PDF), Sticker Sheets (3x7, 3x8), Bulk QR, and Backup.
"""
import io
import pytest


def test_export_endpoints(client):
    """Test CSV, Excel, PDF history reports and 3x7/3x8 sticker sheets."""
    # Ensure at least 1 QR exists in history
    client.post("/api/v1/qr/generate", json={
        "title": "Export Test QR",
        "qr_type": "url",
        "data": {"url": "https://example.com"},
        "save_to_history": True,
    })

    # CSV
    csv_res = client.get("/api/v1/export/history/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert len(csv_res.content) > 0

    # Excel
    excel_res = client.get("/api/v1/export/history/excel")
    assert excel_res.status_code == 200
    assert len(excel_res.content) > 0

    # PDF
    pdf_res = client.get("/api/v1/export/history/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 0

    # 3x7 Sticker Sheet
    sheet_3x7 = client.post("/api/v1/export/sticker-sheet?layout=3x7")
    assert sheet_3x7.status_code == 200
    assert sheet_3x7.headers["content-type"] == "application/pdf"
    assert len(sheet_3x7.content) > 0

    # 3x8 Sticker Sheet
    sheet_3x8 = client.post("/api/v1/export/sticker-sheet?layout=3x8")
    assert sheet_3x8.status_code == 200
    assert sheet_3x8.headers["content-type"] == "application/pdf"
    assert len(sheet_3x8.content) > 0


def test_bulk_generation_workflow(client):
    """Upload CSV and process batch QR generation."""
    csv_content = b"url,title\nhttps://alpha.com,Alpha\nhttps://beta.com,Beta\nhttps://gamma.com,Gamma\n"
    file = io.BytesIO(csv_content)

    upload_res = client.post(
        "/api/v1/bulk/upload",
        files={"file": ("batch.csv", file, "text/csv")},
        data={"qr_type": "url", "job_name": "Test Batch Job"},
    )
    assert upload_res.status_code == 200
    job = upload_res.json()
    assert job["total_rows"] == 3
    assert job["processed_rows"] == 3
    assert job["status"] == "completed"
    job_id = job["id"]

    # Download batch ZIP
    dl_res = client.get(f"/api/v1/bulk/{job_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/zip"
    assert len(dl_res.content) > 0


def test_bulk_cancellation_and_stream(client, db_session):
    """Test bulk cancellation endpoint and progress streaming."""
    from app.models import QRBulkJob

    # 1. Create a job in processing state
    active_job = QRBulkJob(
        job_name="In-Progress Queue Job",
        source_filename="queue_test.csv",
        total_rows=100,
        processed_rows=25,
        status="processing",
        qr_type="url",
    )
    db_session.add(active_job)
    db_session.commit()
    db_session.refresh(active_job)
    job_id = active_job.id

    # 2. Test cancel endpoint
    cancel_res = client.post(f"/api/v1/bulk/{job_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # 3. Test SSE stream endpoint receives terminal event
    stream_res = client.get(f"/api/v1/bulk/{job_id}/stream")
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
    assert b"cancelled" in stream_res.content



def test_backup_and_restore_workflow(client):
    """Test full backup creation and restoration."""
    create_res = client.post("/api/v1/backup/", json={"backup_type": "db"})
    assert create_res.status_code == 200
    backup = create_res.json()
    assert backup["status"] == "success"
    backup_id = backup["id"]

    # List backups
    list_res = client.get("/api/v1/backup/")
    assert list_res.status_code == 200
    assert any(b["id"] == backup_id for b in list_res.json())

    # Restore backup
    restore_res = client.post(f"/api/v1/backup/{backup_id}/restore")
    assert restore_res.status_code == 200
    assert restore_res.json()["success"] is True
