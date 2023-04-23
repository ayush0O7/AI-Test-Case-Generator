# Import necessary libraries
import os
import spacy
import queue
import threading
from spacy.lang.en import English
from bs4 import BeautifulSoup
from queue import Queue

# Load the English language model for NLP
nlp = spacy.load("en_core_web_sm")

# Set up OpenAI API key and Flask app
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the index route
@app.route("/", methods=("GET", "POST"))
def index():
    # If form is submitted with POST request
    if request.method == "POST":

        # Get the product requirements from URL or form input
        requirements = get_requirements_from_url(request.form["requirements"]) if is_url(request.form["requirements"]) else request.form["requirements"]

        # Generate initial prompt for requirements summary
        initial_prompt = "Generate requirements for a product whose brief description is : " + request.form["product_description"] +" Whose users are: "+request.form["user_description"]+" Whose product requirements document is: "
        initial_prompt+=requirements

        # Get the requirements summary
        requirements_summary = get_summary(initial_prompt)

        # Generate initial prompt for test cases summary
        initial_prompt = "Generate test cases for a product whose requirements are : "
        initial_prompt+=requirements_summary

        # Get the test cases summary
        test_cases_summary = get_summary(initial_prompt)

        # Redirect to the index page with the result
        return redirect(url_for("index", result=test_cases_summary))

    # If form is not submitted, render the index page
    result = request.args.get("result")
    return render_template("index.html", result=result)

def is_url(string):
    import re
    # Regular expression pattern to match a URL
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

    # Match the pattern with the string
    match = pattern.match(string)

    # Return True if the string is a valid URL, False otherwise
    return bool(match)

# This function checks if a given string is a valid URL or not using regular expression matching.
def get_requirements_from_url(url):
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        with webdriver.Chrome('./chromedriver', options=options) as driver:
          driver.get(url)
          html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        return text

#This function takes a URL as input, uses Selenium to fetch the HTML content of the webpage, 
# and extracts the text content from it using the BeautifulSoup library. It returns the extracted text.
def get_summary(text):
    requirement_chunks = requirements_to_chunks(text)
    final_requirements = []
    response_queue = Queue()
    threads = []

    for chunk in requirement_chunks:
        # Start a new thread to generate requirements for each chunk of text
        thread = threading.Thread(target=generate_requirements, args=(" ".join(chunk), response_queue))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect the responses from the queue and join them to form the final summary
    while not response_queue.empty():
        response = response_queue.get()
        final_requirements.append(response['choices'][0]['message']['content'])

    summary = " ".join(final_requirements)
    return summary

#This function takes a chunk of text as input, generates requirements using OpenAI's GPT-3 model, and adds the response to a queue to be collected by the get_summary function.
# It uses various parameters such as temperature, max_tokens, top_p, frequency_penalty, and presence_penalty to customize the behavior of the GPT-3 model.
def generate_requirements(text,response_queue):
    prompt = f"{text}"

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": prompt}],  
      temperature=0.1, 
      max_tokens=RESPONSE_SIZE, # = no. of words in response -- for requirements
      top_p=1, 
      frequency_penalty=0,
      presence_penalty=1
    )
    response_queue.put(response)

#This function takes in a string of text and breaks it down into smaller chunks based on the CHUNK_SIZE constant defined in the code. 
# It uses the spacy NLP library to parse the input text and split it into sentences. 
# It then loops through each sentence and keeps track of the word count for the current chunk. 
# If the word count exceeds the CHUNK_SIZE, it creates a new empty chunk and starts adding sentences to it. 
# Finally, it returns a list of chunks, where each chunk is a list of sentences.
def requirements_to_chunks(text):
  chunks = [[]] # Initialize an empty list of chunks
  chunk_total_words = 0 # Initialize the word count for the current chunk

  sentences = nlp(text) # Parse the input text using the spacy NLP library

  for sentence in sentences.sents: # Loop through each sentence in the parsed text
    chunk_total_words += len(sentence.text.split(" ")) # Update the word count for the current chunk

    if chunk_total_words > CHUNK_SIZE: # If the current chunk has exceeded the maximum size
      chunks.append([]) # Create a new empty chunk
      chunk_total_words = len(sentence.text.split(" ")) # Reset the word count for the new chunk

    chunks[len(chunks)-1].append(sentence.text) # Add the current sentence to the current chunk
  
  return chunks # Return the list of chunks

CHUNK_SIZE=500
RESPONSE_SIZE=1500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, debug=True)    
    