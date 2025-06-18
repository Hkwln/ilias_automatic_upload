import os
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# --- CONFIGURATION ---
UPLOAD_FOLDER = "upload"
ID_FILE = "id.txt"
ILIAS_URL = "https://ilias3.uni-stuttgart.de/login.php?cmd=force_login&client_id=Uni_Stuttgart&lang=de"  # Change to your ILIAS URL

# Map keywords to (group_name, submission_name, url or navigation function)
FILENAME_TO_GROUP = {
    "math": ("Mathe für Informatiker 2", "Übung 7", None),
    "theoretical": ("Theoretische Informatik", "Übung 3", None),
    # Add more mappings as needed
}

# --- UTILITIES ---
def read_credentials(id_file):
    with open(id_file, "r") as f:
        lines = f.read().splitlines()
        if len(lines) < 2:
            raise Exception("id.txt must contain username and password on separate lines.")
        return lines[0], lines[1]

def match_file_to_group(filename):
    name = filename.lower()
    # Only handle math for now
    import re
    match = re.search(r"mathe2_blatt(\d+)", name)
    if match:
        blatt_num = match.group(1)
        group = "Mathematik für Informatikstudiengänge II (Gruppenübungen)"
        subgroup = "Gruppe 05"
        abgabe_uebungsblaetter = "Abgabe zu übungsblätter"
        abgabe_blatt = f"Abgabe Blatt {blatt_num}"
        return group, subgroup, abgabe_uebungsblaetter, abgabe_blatt
    return None, None, None, None

# --- SELENIUM AUTOMATION ---
def ilias_login(driver, username, password):
    driver.get(ILIAS_URL)
    # Use the provided username field selector
    username_field = driver.find_element(By.NAME, "login_form/input_3/input_4")
    username_field.clear()
    username_field.send_keys(username)
    # Try common patterns for password field
    try:
        password_field = driver.find_element(By.NAME, "login_form/input_3/input_5")
    except NoSuchElementException:
        # Fallback: try input[type='password']
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
    password_field.clear()
    password_field.send_keys(password)
    # Submit by pressing ENTER in the password field
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

def click_link_text(driver, text):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Wait for the link to be present
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, text))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", link)
    time.sleep(0.5)
    try:
        link.click()
    except Exception:
        # Fallback: click with JS if intercepted
        driver.execute_script("arguments[0].click();", link)
    time.sleep(1)

def click_group05_and_abgabe(driver, subgroup):
    # Click "Gruppe 05" link
    click_link_text(driver, subgroup)
    time.sleep(1)
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    abgabe_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ilListItemSection') and contains(text(), 'Bitte laden Sie hier Ihre schriftliche Abgaben hoch!')]"))
    )
    # Find the closest ancestor with class il_ContainerListItem
    container = abgabe_div.find_element(By.XPATH, "ancestor::div[contains(@class, 'il_ContainerListItem')][1]")
    # Find the <a> inside <h3 class="il_ContainerItemTitle">
    abgabe_link = container.find_element(By.XPATH, ".//h3[contains(@class, 'il_ContainerItemTitle')]/a")
    driver.execute_script("arguments[0].scrollIntoView(true);", abgabe_link)
    time.sleep(0.5)
    try:
        abgabe_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", abgabe_link)
    time.sleep(1)

def navigate_and_upload_math(driver, group, subgroup, abgabe_uebungsblaetter, abgabe_blatt, filepath):
    try:
        click_link_text(driver, group)
        click_group05_and_abgabe(driver, subgroup)
        click_link_text(driver, abgabe_blatt)
        # Debug: print all button and link texts before searching for upload
        print("[DEBUG] All button texts on page:")
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            print(btn.text)
        print("[DEBUG] All link texts on page:")
        for a in driver.find_elements(By.TAG_NAME, "a"):
            print(a.text)
        # Try clicking 'Einreichung' link first
        links = driver.find_elements(By.TAG_NAME, "a")
        found = False
        for link in links:
            if link.text.strip() == "Einreichung":
                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(0.5)
                try:
                    link.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", link)
                time.sleep(1)
                found = True
                break
        # If not found, try 'Abgabe der Übungsblätter' button
        if not found:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if btn.text.strip() == "Abgabe der Übungsblätter":
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    try:
                        btn.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                    found = True
                    break
        if not found:
            print("[DEBUG] Could not find 'Einreichung' link or 'Abgabe der Übungsblätter' button. Printing all button and link HTML for further debugging:")
            for btn in buttons:
                print(driver.execute_script("return arguments[0].outerHTML;", btn))
            for link in links:
                print(driver.execute_script("return arguments[0].outerHTML;", link))
            raise NoSuchElementException("Neither 'Einreichung' nor 'Abgabe der Übungsblätter' found.")
        # Continue with the rest of the workflow as before...
        # Click "Datei hochladen"
        hochladen_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Datei hochladen')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", hochladen_btn)
        time.sleep(0.5)
        try:
            hochladen_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", hochladen_btn)
        time.sleep(1)
        # Click "Dateien wählen"
        waehlen_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Dateien wählen')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", waehlen_btn)
        time.sleep(0.5)
        try:
            waehlen_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", waehlen_btn)
        time.sleep(1)
        # Upload file
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(os.path.abspath(filepath))
        time.sleep(2)  # Wait for upload
        # Click "Speichern"
        speichern_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Speichern')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", speichern_btn)
        time.sleep(0.5)
        try:
            speichern_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", speichern_btn)
        print(f"Uploaded {filepath} to {abgabe_blatt}")
    except NoSuchElementException as e:
        print(f"Error: Could not find navigation element. {e}")
        driver.get(ILIAS_URL)
        print("Redirected to ILIAS main page for manual upload.")

# --- WATCHDOG HANDLER ---
class UploadHandler(FileSystemEventHandler):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            filename = os.path.basename(event.src_path)
            group, subgroup, abgabe_uebungsblaetter, abgabe_blatt = match_file_to_group(filename)
            print(f"Detected new file: {filename}")
            if group:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                self.driver = webdriver.Chrome(options=chrome_options)
                try:
                    ilias_login(self.driver, self.username, self.password)
                    navigate_and_upload_math(self.driver, group, subgroup, abgabe_uebungsblaetter, abgabe_blatt, event.src_path)
                finally:
                    self.driver.quit()
            else:
                print("Error: Could not determine math submission for file.")
                # Optionally open ILIAS main page for manual upload

# --- MAIN ---
def main():
    username, password = read_credentials(ID_FILE)
    event_handler = UploadHandler(username, password)
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_FOLDER, recursive=False)
    observer.start()
    print(f"Monitoring {UPLOAD_FOLDER} for new PDF files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
