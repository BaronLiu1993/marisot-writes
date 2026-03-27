from app_queue.file.fileIngestionQueue import celery_app


@celery_app.task(name="app_queue.file.fileIngestionWorker.process_file_from_s3")
def process_file_from_s3():
	pass
