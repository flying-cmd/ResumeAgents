# Interview Question Bank

## Project Deep-Dive Questions

**Q1: In your RAG Intelligent Customer Service System project, you mentioned processing millions of historical QA records to evaluate accuracy and recall. Can you walk me through the specific architecture you designed for this data ingestion pipeline, particularly focusing on how you handled the "resumable processing" requirement for large batch tasks to prevent failure?**

*Detailed Answer:*
For the RAG system's data ingestion pipeline, we faced significant challenges due to the volume of data (millions of records) and the computational cost of generating embeddings. To address this, I designed an asynchronous batch processing architecture using **Celery** workers orchestrated within our **Kubernetes** cluster, driven by **FastAPI** endpoints for triggering jobs.

The core challenge was ensuring data integrity without locking up the system if a job failed mid-process. To implement "resumable processing," I implemented a checkpoint-based state management system stored in our **MySQL** database. Instead of processing all records in a single transaction, I divided the dataset into manageable chunks (e.g., 10,000 records per task). Each chunk had a unique ID and a status field (Pending, Processing, Completed, Failed).

When a worker picked up a chunk, it updated the status to 'Processing'. If the task encountered an exception—such as a network timeout during embedding generation or a memory spike—the Celery retry mechanism would catch the error. Crucially, before retrying, the system checked the checkpoint. Since the chunk ID was already marked as 'Processing' or 'Failed', the worker could resume from the last successful record within that chunk rather than restarting from zero. We also utilized **idempotent operations** for the vector insertion into **Elasticsearch**; if a duplicate vector was generated during a retry, the upsert operation ensured no data duplication occurred.

To optimize performance, I implemented a sliding window approach where multiple Celery workers processed different chunks in parallel, limited by the GPU resources available for the embedding model. We monitored queue depths and worker CPU usage via Prometheus to auto-scale the number of workers dynamically. This approach reduced the total ingestion time significantly compared to a sequential run and ensured that even if a node crashed, the overall pipeline could recover and complete without manual intervention.

