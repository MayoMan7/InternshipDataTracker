import requests
from bs4 import BeautifulSoup
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv
import os


nltk.download('punkt')
nltk.download('stopwords')


def get_job_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith("https://simplify.jobs/p/"):
            job_links.add(href)
    return job_links


def get_job_description(job_url):
    response = requests.get(job_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_description = ""
    for element in soup.find_all(class_='mt-4'):
        job_description += element.get_text(separator=" ")  # Combine text with spaces
    return job_description


def update_word_counts(job_text, word_counts):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(job_text.lower())
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    word_counts.update(filtered_words)


def save_word_counts_to_csv(word_counts, filename="word_counts.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Word", "Count"])
        for word, count in word_counts.items():
            writer.writerow([word, count])


def save_processed_links(processed_links, filename="processed_links.txt"):
    with open(filename, mode='w', encoding='utf-8') as file:
        file.write("\n".join(processed_links))


def load_processed_links(filename="processed_links.txt"):
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            return set(file.read().splitlines())
    return set()


def test_system_with_limited_links(repo_url, limit=5):
    """
    Test the system by processing only the first `limit` job links.
    """
    processed_links_file = "processed_links_test.txt"
    word_counts_file = "word_counts_test.csv"

    # Load already processed links
    processed_links = load_processed_links(processed_links_file)
    print(processed_links)

    # Get all job links
    job_links = get_job_links(repo_url)
    new_links = list(job_links - processed_links)[:limit]  # Process only `limit` links
    print("PROCESSED LINKS")
    print(processed_links)
    print("NEW LINKS")
    print(new_links)

    # Initialize word counts
    word_counts = Counter()

    # Process limited job links
    for link in new_links:
        try:
            print(f"Processing: {link}")  # Debug output
            job_description = get_job_description(link)
            update_word_counts(job_description, word_counts)
            processed_links.add(link)
        except Exception as e:
            print(f"Failed to process {link}: {e}")

    # Save updated word counts and processed links
    save_word_counts_to_csv(word_counts, word_counts_file)
    save_processed_links(processed_links, processed_links_file)
    print(f"Test word counts saved to {word_counts_file}")
    print(f"Test processed links saved to {processed_links_file}")

# Main script
def main():
    repo_url = "https://github.com/SimplifyJobs/Summer2025-Internships"
    processed_links_file = "processed_links.txt"
    word_counts_file = "word_counts.csv"

    # Load already processed links
    processed_links = load_processed_links(processed_links_file)

    # Get all job links
    job_links = get_job_links(repo_url)
    new_links = job_links - processed_links

    # Initialize word counts
    word_counts = Counter()

    # Process new job links
    for link in new_links:
        try:
            job_description = get_job_description(link)
            update_word_counts(job_description, word_counts)
            print(f"Processed: {link}")
            processed_links.add(link)
        except Exception as e:
            print(f"Failed to process {link}: {e}")
    print(f"Processed {len(new_links)} new links")

    # Save updated word counts and processed links
    save_word_counts_to_csv(word_counts, word_counts_file)
    save_processed_links(processed_links, processed_links_file)
    print(f"Word counts saved to {word_counts_file}")
    print(f"Processed links saved to {processed_links_file}")


if __name__ == "__main__":
    # test_system_with_limited_links("https://github.com/SimplifyJobs/Summer2025-Internships",5)
    main()
