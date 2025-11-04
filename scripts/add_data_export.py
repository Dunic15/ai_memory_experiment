"""
Add data export functionality to app.py
This allows downloading all experiment data from cloud deployments
"""

# Add this to app.py after the existing routes

@app.route("/admin/export", methods=["GET"])
def admin_export_data():
    """
    Export all experiment data as ZIP file.
    Requires ADMIN_KEY environment variable for security.
    """
    admin_key = os.environ.get("ADMIN_KEY")
    provided_key = request.args.get("key")
    
    if not admin_key or provided_key != admin_key:
        return jsonify({"error": "Unauthorized"}), 403
    
    import zipfile
    import tempfile
    from flask import send_file
    
    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    zip_path = temp_zip.name
    temp_zip.close()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all CSV files
        if os.path.exists(DATA_DIR):
            for filename in os.listdir(DATA_DIR):
                if filename.endswith('.csv'):
                    filepath = os.path.join(DATA_DIR, filename)
                    zipf.write(filepath, filename)
        
        # Add translation cache if needed
        if os.path.exists(TRANSLATION_CACHE_FILE):
            zipf.write(TRANSLATION_CACHE_FILE, 'translations.json')
    
    # Send file
    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'experiment_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    )

@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    """
    Get statistics about experiment data.
    Requires ADMIN_KEY environment variable.
    """
    admin_key = os.environ.get("ADMIN_KEY")
    provided_key = request.args.get("key")
    
    if not admin_key or provided_key != admin_key:
        return jsonify({"error": "Unauthorized"}), 403
    
    stats = {
        "participant_count": 0,
        "data_files": [],
        "total_data_size_mb": 0,
        "last_update": None
    }
    
    if os.path.exists(DATA_DIR):
        csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        stats["data_files"] = csv_files
        
        # Count participants
        participants_file = os.path.join(DATA_DIR, "participants.csv")
        if os.path.exists(participants_file):
            with open(participants_file, 'r', encoding='utf-8') as f:
                stats["participant_count"] = sum(1 for line in f) - 1  # Subtract header
        
        # Calculate total size
        total_size = sum(
            os.path.getsize(os.path.join(DATA_DIR, f))
            for f in csv_files
        )
        stats["total_data_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Get last modification time
        if csv_files:
            latest_file = max(
                csv_files,
                key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f))
            )
            stats["last_update"] = datetime.fromtimestamp(
                os.path.getmtime(os.path.join(DATA_DIR, latest_file))
            ).isoformat()
    
    return jsonify(stats)

