import subprocess
""" # Lancer le script Python avec le chemin correct
subprocess.run(["python3", "../../manageReact.py"])

# Exécuter npm start dans une autre instance de terminal
subprocess.run(["gnome-terminal", "--", "npm", "start"]) """
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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


if __name__ == "__main__":
    unittest.main()