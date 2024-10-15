# Airflow Pipeline Project

This repository contains an automated pipeline built using **Apache Airflow**. The pipeline is designed to scrape news articles, perform sentiment analysis, and store the results in a database. Additionally, a static input movie dataset pipeline is included, which processes and stores movie data.

## Features

- **Automated Web Scraping**: Scrapes news articles for specific keywords (HDFC, Tata Motors).
- **Sentiment Analysis**: Performs sentiment analysis on scraped articles.
- **Data Storage**: Stores the final sentiment scores in a PostgreSQL database.
- **CI/CD**: GitHub Actions pipeline for automated deployment and execution.
- **Error Notifications**: Failure notifications are triggered on workflow failures.

## Project Structure

```bash
.
├── dags/                             # Airflow DAGs
├── logs/                             # Log files
├── Dockerfile                        # Docker setup for the project
├── docker-compose.yml                # Docker Compose file to set up the environment
├── .env                              # Environment variables for Airflow
└── .github/workflows/ci.yml          # GitHub Actions workflow for CI/CD

Installation and Setup:
1.Clone the Repository:
git clone https://github.com/shaileshchaudhari17/airflow-pipeline-project.git
cd airflow-pipeline-project

2.Set Up Environment Variables:
Create a .env file in the root directory with the following details:
AIRFLOW__CORE__LOAD_EXAMPLES=False
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db

3.Start the Docker Containers:
docker-compose up --build -d

4.Access the Airflow Web UI:
http://localhost:8080
Username: airflow
Password: airflow

5.Trigger the Pipeline:
After logging into Airflow, trigger the news scraping DAG (news_scraping_pipeline) manually or allow it to run on schedule.

CI/CD Pipeline

This repository is integrated with GitHub Actions to automatically build and run the Airflow pipeline whenever changes are pushed to the repository.

    The workflow file is located at .github/workflows/ci.yml.
    The CI/CD pipeline includes building the Docker containers and running the Airflow DAGs automatically.

Alerts on Failure

In case of a failure during the workflow execution, an automated failure notification is triggered.

