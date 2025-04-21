from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # HTML form to get URLs

@app.route('/run-selenium', methods=['POST'])
def run_selenium():
    # Get URLs from the form input
    service_url = request.form['serviceUrl']
    customer_url = request.form['customerUrl']

    # Pass these URLs to the Selenium scraping code
    scrape_message = scrape_facebook_posts(service_url, customer_url)
    return render_template('leads.html', message=scrape_message)

def scrape_facebook_posts(service_url, customer_url):
    # Selenium script starts here
    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        # Navigate to Facebook login page
        driver.get('http://www.facebook.com')

        # Login to Facebook
        username = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
        username.clear()
        username.send_keys("aroobaminhas14@gmail.com")  # Replace with your email
        password.clear()
        password.send_keys("beautyinsights")  # Replace with your password
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        time.sleep(5)

        # Navigate to the customer URL (dynamically passed)
        driver.get(customer_url)
        time.sleep(5)

        all_posts = []

        # Scrape posts
        for _ in range(3):  # Adjust the number of scrolls if needed
            try:
                posts = driver.find_elements(By.XPATH, "//*[contains(@data-ad-comet-preview, 'message')]")
                for post in posts:
                    try:
                        # Check and click the "See more" button if it exists
                        try:
                            see_more_button = post.find_element(By.XPATH, ".//div[contains(text(), 'See more')]")
                            driver.execute_script("arguments[0].click();", see_more_button)
                            time.sleep(1)
                        except NoSuchElementException:
                            pass

                        # Collect inner div text elements within each post
                        post_text_parts = post.find_elements(By.XPATH, ".//div[@style='text-align: start;']")
                        post_text = " ".join([part.text for part in post_text_parts if part.text])

                        # Extract post ID
                        try:
                            post_id = post.get_attribute("id")
                        except NoSuchElementException:
                            post_id = None

                        if post_text:
                            all_posts.append({'Post': post_text, 'Post ID': post_id})
                    except StaleElementReferenceException:
                        continue

            except StaleElementReferenceException:
                continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Save posts to a CSV file
        df_posts = pd.DataFrame(all_posts)
        df_posts.to_csv('facebook_page_posts_with_ids.csv', index=False)

        return "Scraping complete! Posts saved to facebook_page_posts_with_ids.csv."

    except Exception as e:
        return f"An error occurred: {str(e)}"

    finally:
        driver.quit()

@app.route('/find-leads', methods=['POST'])
def find_leads():
    # Placeholder function for finding leads
    leads_message = "I will find leads soon."
    return render_template('comment.html', message=leads_message)

@app.route('/automate-comment', methods=['POST'])
def automate_comment():
    # Placeholder function for adding a comment
    comment_message = "Comment added."
    return render_template('thankyou.html', message=comment_message)

if __name__ == '__main__':
    app.run(debug=True)
