from fastapi import HTTPException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import asyncio
from app.domain import Job, ScraperStatus


def run_crawler(job_id: str, crawler_request: object) -> None:
    # Create a Selenium WebDriver instance
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver_linux64/chromedriver")

    try:
        # Navigate to the login page
        driver.get("http://extratoclube.com.br/")
        # assert "Extrato Clube - Cliente - Acesso" in driver.title

        login_input = driver.find_element(By.NAME, "usuario")
        login_input.send_keys(crawler_request.login)

        password_input = driver.find_element(By.NAME, "senha")
        password_input.send_keys(crawler_request.password)
        password_input.send_keys(Keys.RETURN)

        # Wait for the dashboard page to load
        # await asyncio.sleep(10)

        # Fill in the login form and submit it
        cpf_input = driver.find_element(By.NAME, "ion-input-31")
        cpf_input.send_keys(str(crawler_request.cpf))
        cpf_input.send_keys(Keys.RETURN)

        bn = driver.find_element(By.TAG_NAME, 'ion-label')

        # Update the job status to "completed" in Redis
        Job.update_by_id(job_id=job_id, state=ScraperStatus.COMPLETED.value, client_benefit_number=bn)

    except Exception as e:
        # Update the job status to "failed" in Redis
        Job.update_by_id(job_id=job_id, state=ScraperStatus.FAILED.value)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the WebDriver instance
        driver.quit()
