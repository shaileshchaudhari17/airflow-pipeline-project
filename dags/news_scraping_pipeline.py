from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import random
import requests
from bs4 import BeautifulSoup
import psycopg2  # Import psycopg2

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'news_scraping_pipeline',
    default_args=default_args,
    description='A pipeline to scrape, clean, and analyze news articles',
    schedule_interval='0 19 * * 1-5',  # Schedule for 7 PM every working day
)

# Step 1: Scrape task
def scrape_task(**context):
    keywords = ['HDFC', 'Tata Motors']
    articles = []

    # Scraping from YourStory
    for keyword in keywords:
        print(f"Scraping articles for {keyword} from YourStory...")
        response = requests.get(f'https://yourstory.com/search?query={keyword}')
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract articles based on the HTML structure of the site
        for article in soup.find_all('div', class_='article-class'):  # Update this class based on actual site
            title = article.find('h2').text  # Update as needed
            link = article.find('a')['href']  # Update as needed
            articles.append({'title': title, 'link': link})

        print(f"Scraped {len(articles)} articles from YourStory.")

        # Scraping from Finshots
        print(f"Scraping articles for {keyword} from Finshots...")
        response = requests.get(f'https://finshots.in/?s={keyword}')
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract articles based on the HTML structure of Finshots
        for article in soup.find_all('article'):
            title = article.find('h2').text  # Adjust this to the actual HTML structure
            link = article.find('a')['href']  # Adjust this to the actual HTML structure
            articles.append({'title': title, 'link': link})

        print(f"Scraped {len(articles)} articles from Finshots.")

    # Limit to the latest 5 articles for each keyword
    articles = articles[:5]

    print(f"Total articles scraped: {len(articles)}")
    return articles


# Step 2: Clean and deduplicate task
def clean_data_task(**context):
    articles = context['ti'].xcom_pull(task_ids='scrape_task')
    
    if not articles:
        raise ValueError("No articles found to clean")
    
    seen_titles = set()
    cleaned_articles = []
    
    for article in articles:
        title = article.get('title')
        if title and title not in seen_titles:
            seen_titles.add(title)
            cleaned_articles.append(article)

    print(f"Before cleaning: {len(articles)} articles")
    print(f"After cleaning: {len(cleaned_articles)} articles")
    
    return cleaned_articles

# Step 3: Sentiment analysis task
def sentiment_analysis_task(**context):
    cleaned_articles = context['ti'].xcom_pull(task_ids='clean_data_task')
    
    if not cleaned_articles:
        raise ValueError("No articles found for sentiment analysis")
    
    # Mock sentiment analysis by assigning a random sentiment score
    for article in cleaned_articles:
        article['sentiment_score'] = round(random.uniform(0, 1), 2)

    print(f"Sentiment analysis completed for {len(cleaned_articles)} articles")
    
    return cleaned_articles

# Step 4: Store the results in PostgreSQL task
def store_results_task(**context):
    analyzed_articles = context['ti'].xcom_pull(task_ids='sentiment_analysis_task')
    
    if not analyzed_articles:
        raise ValueError("No analyzed articles to store in the database")
    
    connection = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres"
    )
    
    cursor = connection.cursor()

    for article in analyzed_articles:
        cursor.execute("""
            INSERT INTO news_sentiment (title, link, sentiment_score)
            VALUES (%s, %s, %s)
        """, (article['title'], article['link'], article['sentiment_score']))

    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"Stored {len(analyzed_articles)} articles in the database.")

# Define the tasks
scrape_task = PythonOperator(
    task_id='scrape_task',
    python_callable=scrape_task,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='clean_data_task',
    python_callable=clean_data_task,
    dag=dag,
)

sentiment_task = PythonOperator(
    task_id='sentiment_analysis_task',
    python_callable=sentiment_analysis_task,
    dag=dag,
)

store_task = PythonOperator(
    task_id='store_results_task',
    python_callable=store_results_task,
    dag=dag,
)

# Update the task dependencies
scrape_task >> clean_task >> sentiment_task >> store_task
