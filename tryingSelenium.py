from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta


def initialize_browser():
    # Initialize browser and actions
    browser = webdriver.Chrome()
    return browser, ActionChains(browser)


def login_to_twitter(browser, wait, username_str, password_str, verification_str=None):
    try:
        # Open Twitter login page
        browser.get("https://x.com/i/flow/login")

        # Enter username and navigate to the next step
        username = wait.until(EC.presence_of_element_located((By.NAME, 'text')))
        username.send_keys(username_str)
        print("Username input found and value sent.")

        # Locate and click the 'Next' button
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button.click()
        print("Next button clicked.")

        # Handle additional verification if verification input is found
        verification_input = None
        try:
            verification_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-text-id='ocfEnterTextTextInput']")))
        except Exception:
            print("No additional verification step found.")

        if verification_input:
            verification_input.send_keys(verification_str)
            next_button_verification = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
            next_button_verification.click()

    except Exception as e:
        print(f"Error during login: {e}")
        browser.quit()
        return False

    try:
        # Enter password
        password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password.send_keys(password_str)
        print("Password input found and value sent.")

        # Click the 'Log in' button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']")))
        login_button.click()
        print("Log in button clicked.")
        return True
    except Exception as e:
        print(f"Error during password input: {e}")
        browser.quit()
        return False


def search_twitter(browser, wait, search_term, start_date, end_date):
    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="SearchBox_Search_Input"]')))
        search_box.click()
        # Clear the search box by selecting all text and deleting
        search_box.send_keys(Keys.CONTROL + 'a')
        search_box.send_keys(Keys.DELETE)
        # Format the search term with the date range
        search_query = f"{search_term} since:{start_date} until:{end_date}"
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        print(f"Search term entered: {search_query}")
        time.sleep(5)  # Give time for search results to load
    except Exception as e:
        print(f"Error during search: {e}")
        browser.quit()


def collect_tweets(browser):
    tweets = []
    try:
        match = False
        while not match:
            # Collect tweets from the current view
            try:
                tweet_elements = browser.find_elements(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                for tweet_element in tweet_elements:
                    tweet_text_parts = tweet_element.find_elements(By.XPATH, ".//span")
                    tweet_text = " ".join([part.text for part in tweet_text_parts])
                    if tweet_text not in tweets and tweet_text.strip() != "":
                        tweets.append(tweet_text)
                        print(tweet_text)
            except Exception as e:
                print(f"Error occurred while collecting tweets. Details: {e}")

            # Scroll to load more tweets
            last_count = browser.execute_script("return document.body.scrollHeight")
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow time for new tweets to load
            len_of_page = browser.execute_script("return document.body.scrollHeight")

            # Check if scrolling resulted in new content
            if last_count == len_of_page:
                match = True

        print("Scrolling completed.")
    except Exception as e:
        print(f"Error occurred while scrolling or collecting tweets. Details: {e}")
        browser.quit()

    return tweets


def save_tweets_to_file(tweets, filename="tweets.txt"):
    try:
        with open(filename, "a", encoding="UTF-8") as file:
            tweet_count = 1
            for tweet in tweets:
                file.write(str(tweet_count) + ".\n" + tweet + "\n")
                file.write("**************************\n")
                tweet_count += 1

        print(f"{len(tweets)} tweets have been collected and appended to '{filename}'.")
    except Exception as e:
        print(f"Error occurred while writing tweets to file. Details: {e}")


def main():
    # User credentials and details
    username_str = "_UtkarshAg"
    password_str = "Utkarsh123#"
    verification_str = "8336902153"
    search_term = "zomato"

    # Initialize browser and WebDriverWait
    browser, actions = initialize_browser()
    wait = WebDriverWait(browser, 15)

    # Login to Twitter
    if login_to_twitter(browser, wait, username_str, password_str, verification_str):
        # Start collecting tweets in 5-day intervals until current date
        all_tweets = []
        start_date = datetime.now() - timedelta(days=25)
        current_date = datetime.now()
        while start_date < current_date:
            end_date = start_date + timedelta(days=5)
            if end_date > current_date:
                end_date = current_date
            search_twitter(browser, wait, search_term, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

            # Collect tweets and add to all_tweets
            tweets = collect_tweets(browser)
            all_tweets.extend(tweets)

            # Update start_date for the next 5-day interval
            start_date = end_date

        # Save all tweets to a single file
        save_tweets_to_file(all_tweets)

        # Close the browser
        browser.quit()


if __name__ == "__main__":
    main()
