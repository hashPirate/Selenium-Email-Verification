from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, string, random, re
import requests
from humanfriendly import format_timespan

accountsFile = "accounts.txt"

with open(accountsFile) as f:
    accounts = list(filter(lambda k: k != '' and '>>>> DONE' not in k, f.read().split("\n")))

    accounts = list(map(lambda k: k.split(" | ")[0], accounts)) # ignoring recovery email & GC number

domains = requests.get('https://www.1secmail.com/api/v1/?action=getDomainList').json()

print("Launching webdriver...")

capabilities = webdriver.DesiredCapabilities.CHROME
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options, desired_capabilities=capabilities)

wait = WebDriverWait(driver, 30)

start_number = 1

for account in accounts:
    username, password = account.split(":")
    print(account)

    t1 = time.perf_counter()

    while True:

        driver.get("https://www.microsoft.com/rpsauth/v1/account/SignIn?ru=https%3A%2F%2Fwww.microsoft.com%2Fen-gb%2F")
        time.sleep(1.00)
        if "SignIn" not in driver.current_url:
            continue
        break

    # Enter email
    wait.until(EC.visibility_of_element_located((By.ID, "i0116"))).send_keys(username)
    # Click Next
    wait.until(EC.visibility_of_element_located((By.ID, "idSIButton9"))).click()

    # Enter password
    wait.until(EC.visibility_of_element_located((By.ID, "i0118"))).send_keys(password)
    # Click Next
    wait.until(EC.visibility_of_element_located((By.ID, "idSIButton9"))).click()

    while True:

        driver.get('https://account.live.com/proofs/manage/additional?mkt=en-US&refd=account.microsoft.com&refp=security')

        securityEmail = f"{''.join(random.sample(string.ascii_lowercase + string.digits, random.randint(8, 12)))}@{random.choice(domains)}"
        secEmail = securityEmail.split('@') # unused for now

        # Enter Security Email
        wait.until(EC.visibility_of_element_located((By.ID, "EmailAddress"))).send_keys(securityEmail)
        # Click Next
        wait.until(EC.visibility_of_element_located((By.ID, "iNext"))).click()

        time.sleep(5.00)
        try:
            msg_id = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={sec_email[0]}&domain={sec_email[1]}", timeout=5).json()[0]['id']
            email_body = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={sec_email[0]}&domain={sec_email[1]}&id={msg_id}", timeout=5).json()['textBody']
            code = re.search("Security code: [0-9]+", email_body)[0][15:]
        except:
            time.sleep(5.00)
            continue
        break

    # Enter Code
    wait.until(EC.visibility_of_element_located((By.ID, "iOttText"))).send_keys(code)
    # Click Next
    wait.until(EC.visibility_of_element_located((By.ID, "iNext"))).click()

    # Save credentials to file
    with open(f"generated.txt", "a") as f:
        f.write(f"{start_number} - {username}:{password} | {securityEmail}\n")

    print(f"Added security email >>>> {username}:{password} | {securityEmail} in {format_timespan(time.perf_counter()-t1)}")

    time.sleep(2.50)

    driver.delete_all_cookies()

    old_window = driver.window_handles[0]
    driver.execute_script("window.open('');")
    new_window = driver.window_handles[1]
    driver.switch_to.window(old_window)
    driver.close()
    driver.switch_to.window(new_window)

    time.sleep(1.00)

    driver.get("https://www.microsoft.com/rpsauth/v1/account/SignOut?ru=https%3A%2F%2Fwww.microsoft.com%2Fen-gb%2F")

    WebDriverWait(driver, 20000).until(EC.visibility_of_element_located((By.ID, "uhfLogo")))

    time.sleep(1.00)

    start_number += 1