from playwright.sync_api import Page, expect

class Login:
    """
    Handles login interactions on the Ultimatix login page.
    """

    def __init__(self, page: Page):
        """
        Initialize locators for login elements.

        Args:
            page (Page): Playwright page object.
        """
        self.page = page
        self.user_name = page.get_by_role("textbox", name="Enter username and, on Tab")
        self.proceed_button = page.get_by_role("button", name="Press enter key to Proceed or")
        self.easy_auth = page.get_by_role("button", name="Press Enter for EasyAuth, or")

    def enter_username(self, username: str) -> None:
        """
        Fill in the username field and click the proceed button.

        Args:
            username (str): Employee username.
        """
        self.user_name.fill(username)
        self.proceed_button.click()

    def easyauth(self) -> None:
        """
        Perform EasyAuth login by clicking the EasyAuth button.
        """
        expect(self.easy_auth).to_be_visible()
        self.easy_auth.click()

    def get_digits(self) -> str:
        """
        Retrieve the validation digits displayed on the page.

        Returns:
            str: Validation digits string.
        """
        digits = self.page.get_by_label("The number for validation is")
        return digits.inner_text()

    def login(self, username: str) -> None:
        """
        Perform the full login flow: enter username, EasyAuth, and validate login.

        Args:
            username (str): Employee username.
        """
        self.enter_username(username)
        self.easyauth()
        digits = self.get_digits()
        print(f"🔑 Auth Code is: {digits}")  # Modernized print statement
        expect(self.page).not_to_have_title(
            "Ultimatix - Digitally Connected!", timeout=60000
        )
