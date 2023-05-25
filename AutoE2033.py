from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
import time
import openai

# API Keys
openai.api_key = ""

# XPATHs
challenge_xp = '//*[@id="__next"]/div/div[1]/div/div[2]/main/div/div/div[3]/div/button'
starting_election_xp = '//*[@id="__next"]/div/div[1]/div/div[2]/main/div/div/div[4]/div/button'
play_again_xp = '//*[contains(@id, "headlessui-dialog-panel-:r")]/div/div[5]/button'

# Function to set up global driver instance
def set_up_driver():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    # Attach to the existing Chrome instance
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# GLOBAL DRIVER
driver = set_up_driver()

# Function to input campaign statement
def input_campaign_statement(campaign_statement):
    if is_button_clickable(starting_election_xp):
        starting_election = driver.find_element(By.XPATH, starting_election_xp)
        print("Re-Clicking to Start Challenge")
        starting_election.click()
        return False
    
    time.sleep(3)
    textarea = driver.find_element(By.ID, "comment")
    time.sleep(.5)
    textarea.clear()
    time.sleep(.5)
    textarea.send_keys(" ")
    time.sleep(.5)
    textarea.clear()
    time.sleep(.5)
    print("Campaign Statement Sent to Input.")
    textarea.send_keys(campaign_statement)
    return True

# Function to check if button is clickable by XPATH
def is_button_clickable(xpath):
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return True
    except TimeoutException:
        return False

# Function to start challenge, and handle edge cases
def start_challenge(campaign_statement):
    challenge = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, challenge_xp )))
    
    # Click 'Challenge' Button
    challenge.click()

    time.sleep(1)
    # Check if challenge start failed
    if is_button_clickable(challenge_xp):
        print("Challenge Start FAILED. Retrying...")
        input_campaign_statement(campaign_statement)
        start_challenge(campaign_statement)

# Function to collect feedback from the pannel.
def collect_feedback():
    time.sleep(5)
    Feedback = []
    print("Collecting Feedback...")
    for i in range(5):
        time.sleep(5)
        element = driver.find_element(By.XPATH, '//h2[@class="text-white text-md"]')

        # fetch the text of the element
        Feedback.append(element.text)

    print("Feedback Collected.")

    Feedback.insert(0, Feedback.pop())
    
    FBD = {
            "Snoop Dogg" : Feedback[0],
            "Random Four-Year Old" : Feedback[1],
            "Super Intelligence AI" : Feedback[2],
            "Sentient Goldfish" : Feedback[3],
            "Elon Musk" : Feedback[4]
          }
    
    Feedback = ""
    for i in FBD:
        Feedback += f"{i}: {FBD[i]}\n"
        print(f"{i}: {FBD[i]}\n")
    return Feedback

def E2033(campaign_statement): 
    try:
        # Try to click 'Play Again' button
        play_again_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, play_again_xp)))
        play_again_button.click()
        print("'Play Again' Clicked")
    
    except TimeoutException:
        print("Challenge Ready.")

    #myELO = 
    #compELO = 

    #if myELO <= compELO:
        #driver.refresh()
        #E2033(campaign_statement)


    if input_campaign_statement(campaign_statement):
        start_challenge(campaign_statement)
        print("Challenge Started.")

    # Wait until victory is over
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, play_again_xp)))
    print("Match Over.")

    try:
        driver.find_element(By.XPATH, '//h1[@class="mt-6 text-4xl sm:text-6xl font-medium text-mediumRed text-center"]')
        print("LOSS")
        Feedback = collect_feedback()
        return Feedback
    except NoSuchElementException:
        print("VICTORY")
        time.sleep(2)
        return None


# Function to rebuild campaign statement based on feedback
def Rebuild_Campaign(Feedback, campaign_statement):
    # Check if current campaing statement is winning
    if Feedback is None:
        Feedback = E2033(campaign_statement)
        Rebuild_Campaign(Feedback, campaign_statement)

    print("Generating Re-Engineered Campaign Statement...")

    # System Role Prompt
    system_role = "In the future, only five voters count.\n"
    system_role += "Unleash your most captivating, Tweet-sized campaign statement to sway their minds.\n"
    system_role += "Adapt to their feedback and climb the ranks towards power.\n"
    system_role += "Do you have what it takes to be president for 2033?\n"
    system_role += "Your job is to improve the current campaign statement based on their feedback.\n"
    system_role += "You only have 200 characters, so use your words wisely."
    system_role += "Do not use hashtags or emojis."

    completion = openai.ChatCompletion.create(
        model="gpt-4",

        messages=[
                  {"role": "system", "content": system_role},
                  {"role": "user", "content": f"Current Campaign Statement: {campaign_statement}"},
                  {"role": "user", "content": f"Feeback: {Feedback} New Campaign Statement:"}
                 ], 

        )
    new_campaign_statement = completion['choices'][0]['message']['content'].strip()

    if 150 < len(new_campaign_statement) > 280:
        print(f"ERROR Length of completion: {len(new_campaign_statement)}")
        print(new_campaign_statement)
        Rebuild_Campaign(Feedback, campaign_statement)
    else:
        print(new_campaign_statement)
        Feedback = E2033(new_campaign_statement)
        Rebuild_Campaign(Feedback, new_campaign_statement)

# Main      
if __name__ == "__main__":
    campaign_statement = "Lets save humanity by ridding poverty, hunger, and abuse by integrating creative "
    campaign_statement += "and fun education in all communities, ultimately connecting people back together. "
    campaign_statement += "By doing this we will develop impressive tech for clean energy and exploring space! "
    campaign_statement += "Human-AI Collab will skyrocket!"
    
    Feedback = E2033(campaign_statement)
    Rebuild_Campaign(Feedback, campaign_statement)
