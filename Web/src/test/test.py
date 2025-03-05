import subprocess
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import threading

stop_thread = False

users = [
    {
        "email": "user1@example.com",
        "password": "password1",
        "last_name": "Dupont",
        "first_name": "Jean",
        "address": "10 Rue de Rivoli"
    },
    {
        "email": "user2@example.com",
        "password": "password2",
        "last_name": "Martin",
        "first_name": "Marie",
        "address": "20 Avenue des Champs-Élysées"
    },
    {
        "email": "user3@example.com",
        "password": "password3",
        "last_name": "Bernard",
        "first_name": "Luc",
        "address": "30 Boulevard Saint-Germain"
    },
    {
        "email": "user4@example.com",
        "password": "password4",
        "last_name": "Dubois",
        "first_name": "Sophie",
        "address": "40 Rue de la Paix"
    },
    {
        "email": "user5@example.com",
        "password": "password5",
        "last_name": "Moreau",
        "first_name": "Pierre",
        "address": "50 Rue du Faubourg Saint-Honoré"
    }
]

def run_command(command):
    while not stop_thread:
        subprocess.run(command, shell=True)
        time.sleep(1)
    print("Thread has been stopped.")

class TestUserCreation(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get("http://localhost:3000")
        time.sleep(2)

    def tearDown(self):
        self.driver.quit()

    def test_user_creation_and_login(self):
        driver = self.driver

        inscrire_link = driver.find_element(By.LINK_TEXT, "S'inscrire")
        inscrire_link.click()
        time.sleep(2)

        driver.find_element(By.ID, "email").send_keys("test@exemple.com")
        driver.find_element(By.ID, "password").send_keys("test")
        driver.find_element(By.ID, "last_name").send_keys("Doe")
        driver.find_element(By.ID, "first_name").send_keys("John")
        driver.find_element(By.ID, "address").send_keys("123 Main St")

        is_driver_checkbox = driver.find_element(By.ID, "is_driver")
        if not is_driver_checkbox.is_selected():
            is_driver_checkbox.click()

        driver.find_element(By.CLASS_NAME, "submit-btn").click()

        time.sleep(3)

        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        self.assertTrue(success_message.is_displayed(), "User creation failed or success message not found.")

        time.sleep(3)

        driver.find_element(By.LINK_TEXT, "Connexion").click()
        time.sleep(2)

        driver.find_element(By.ID, "email").send_keys("test@exemple.com")
        driver.find_element(By.ID, "password").send_keys("test")
        driver.find_element(By.CLASS_NAME, "submit-btn").click()

        time.sleep(3)

        element = driver.find_element(By.LINK_TEXT, "Mon EDT")
        assert element.is_displayed(), "Mon EDT not displayed -> login failed."
        self.tearDown()

class TestUserRelation(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get("http://localhost:3000")
        time.sleep(2)

    def tearDown(self):
        self.driver.quit()

    def test_user_relation(self):
        driver = self.driver
        print(f"Il y a {len(users)} utilisateurs à insérer.")
        for user in users:
            driver.find_element(By.LINK_TEXT, "S'inscrire").click()
            time.sleep(5)

            # Wait for the email field to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

            driver.find_element(By.ID, "email").send_keys(user["email"])
            driver.find_element(By.ID, "password").send_keys(user["password"])
            driver.find_element(By.ID, "last_name").send_keys(user["last_name"])
            driver.find_element(By.ID, "first_name").send_keys(user["first_name"])
            driver.find_element(By.ID, "address").send_keys(user["address"])

            is_driver_checkbox = driver.find_element(By.ID, "is_driver")
            if not is_driver_checkbox.is_selected():
                is_driver_checkbox.click()

            driver.find_element(By.CLASS_NAME, "submit-btn").click()
            time.sleep(3)

            success_message = driver.find_element(By.CLASS_NAME, "success-message")
            self.assertTrue(success_message.is_displayed(), f"User creation failed for {user['email']} or success message not found.")

            driver.refresh()



if __name__ == "__main__":
    file_path = '../../instance/users.db'

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted.")
    else:
        print(f"{file_path} does not exist.")

    # Define the commands to be executed
    command1 = "cd ../.. && python3 manageReact.py"
    command2 = "cd ../.. && npm start"

    # Create threads
    thread1 = threading.Thread(target=run_command, args=(command1,))
    thread2 = threading.Thread(target=run_command, args=(command2,))

    thread1.start()
    print("Server is starting...")
    time.sleep(15)
    thread2.start()
    print("React is starting...")
    time.sleep(15)

    unittest.main(exit=False)
    stop_thread = True
    print("Stopping threads...")
    thread1.join()
    thread2.join()