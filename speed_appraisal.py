"""
Automation script for Ultimatix SPEED appraisal workflow.
Handles login, cookie management, appraisal data extraction, and YAML persistence.
"""

import json
import yaml
from pages.ultimatix_login import Login
from pages.speed_page import Speed
from user_flow import create_flow
from playwright.sync_api import Playwright, sync_playwright, expect


def save_cookies(page, filename: str) -> None:
    """
    Save browser cookies to a JSON file.

    Args:
        page: Playwright page object.
        filename (str): Path to the file where cookies will be saved.
    """
    cookies = page.context.cookies()
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(cookies, f)


def load_cookies(page, filename: str) -> None:
    """
    Load cookies from a JSON file and add them to the browser context.

    Args:
        page: Playwright page object.
        filename (str): Path to the file containing cookies.
    """
    with open(filename, "r", encoding="UTF-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        page.context.add_cookies([cookie])


def save_yamls(content: dict, content_name: str, filename: str, extension: str) -> None:
    """
    Save content to a YAML file.

    Args:
        content (dict): Data to be saved.
        content_name (str): Name to append to the file.
        filename (str): Base path for the file.
        extension (str): File extension (e.g., ".yaml").
    """
    with open(filename + content_name + extension, "w", encoding="UTF-8") as f:
        yaml.dump(content, f, sort_keys=False)


def run(play_wright: Playwright) -> None:
    """
    Execute the SPEED appraisal automation workflow.

    Args:
        play_wright (Playwright): Playwright instance used to launch the browser.
    """
    browser = play_wright.chromium.launch(
        headless=False,
        slow_mo=3000,
        traces_dir="./ContinousFeedback/traces",
        devtools=False,
        # record_video_size={"width": 640, "height": 480}
    )
    context = browser.new_context(
        # record_video_dir="./ContinousFeedback/videos/",
        # viewport={ 'width': 1024, 'height': 600 },
    )
    page = context.new_page()
    load_cookies(page, "./ContinousFeedback/cookies.json")

    page.goto("https://speedappraisal.ultimatix.net/performancemgmt/")

    if page.title() == "Ultimatix - Digitally Connected!":
        user = Login(page)
        expect(user.user_name).to_be_visible()
        user.login("") # Employee ID or UserName
        print("✅ Login successful")
        save_cookies(page, "./ContinousFeedback/cookies.json")

    if page.title() == "SPEED - Appraisal":
        speed_page = Speed(page)

        user_details = speed_page.get_associate_details()
        print(f"👤 Retrieved user details: {user_details}")

        speed_page.year_navigation()
        settings = speed_page.get_appraisal_settings()
        print(f"⚙️  Retrieved appraisal settings")

        users = speed_page.get_stackholders()
        print(f"👥 Stakeholders identified")

        feedforward = {"FeedForward": speed_page.start_conversation()}

        settings_dict = {"settings": {setting[0]: setting[1] for setting in settings}}

        users_dict = {
            "stakeholders": [
                {
                    "Name": user_details[0],
                    "Role": user_details[2],
                    "EmpID": user_details[1],
                }
            ]
        }
        for user in users:
            users_dict["stakeholders"].append(
                {"Name": user[1], "Role": user[0], "EmpID": user[2]}
            )

        print("📊 Fetching goals...")
        goals_content = {"Goal(s)": speed_page.get_goals()}
        print("📈 Goals retrieved")

        print("📊 Fetching attributes...")
        attributes_content = {"Attribute(s)": speed_page.get_attributes()}
        print("📈 Attributes retrieved")

        for key, value in {
            "Settings": settings_dict,
            "users_dict": users_dict,
            "feed_forward": feedforward,
            "Goals": goals_content,
            "Attributes": attributes_content,
        }.items():
            save_yamls(value, key, "./ContinousFeedback/details/", ".yaml")

        temp_storage = {}
        create_flow(temp_storage)

        with open(
            "./ContinousFeedback/details/final_comments.yaml", "r", encoding="UTF-8"
        ) as f:
            gaols_and_attributes = f.read()
            comments_data = yaml.safe_load(gaols_and_attributes)

        for element in comments_data:
            print(f"✍🏼 Writing Comments for {list(element.keys())[0]}")
            speed_page.fill_comments(list(element.keys())[0], list(element.values())[0])
    else:
        print(f"❌ Unexpected page title: {page.title()}")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
