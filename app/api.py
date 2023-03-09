from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from app.crawler import run_crawler
from app.domain import Job

api_router = APIRouter()


# Define Pydantic model for request body
class CrawlerRequest(BaseModel):
    cpf: str
    login: str
    password: str


# Endpoint to start the crawler
@api_router.post("/start_crawler")
def start_crawler(crawler_request: CrawlerRequest):
    job = Job(client_cpf=crawler_request.cpf).create()
    # Start the crawler in a separate asyncio task
    # asyncio.create_task(run_crawler(job.job_id, crawler_request))
    run_crawler(job.job_id, crawler_request)
    # Return the job ID as a response
    return JSONResponse(content={"message": "Job created with success", "job_id": job.job_id})


@api_router.get("/check_status")
async def check_crawler_status(job_id: str):
    if not Job.exists(job_id):
        raise HTTPException(status_code=404, detail="Job ID not found")
    # Get the job status from Redis
    job_status = Job.get_by_id(job_id)
    # Return the job status as a response
    return JSONResponse(content={"status": job_status.decode()})
