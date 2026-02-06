import re
from collections import defaultdict
from playwright.sync_api import Page, expect


class Speed:
    """
    Handles page interactions related to appraisal settings, goals, attributes,
    and continuous feedback conversations in the SPEED appraisal system.
    """

    def __init__(self, page: Page):
        """
        Initialize locators for key elements on the SPEED page.

        Args:
            page (Page): Playwright page object.
        """
        self.page = page
        self.basicinfo = page.locator("div.basciCardBody")
        self.associate = page.locator("div.greetingMessage")
        self.conversation = page.get_by_role("button", name="Start Conversation")
        self.view_conversation = page.get_by_role("button", name="View Goal Sheet")
        self.tabs = page.locator("ul.essentialfactorgoal")
        self.cards = page.locator("div.onlyforWebtab").locator("div.cardl")
        self.feedbackcards = page.locator("div.continuousFeedbackCard")

    def listgatherer(self, locator):
        """
        Extract text from a list of locators.

        Args:
            locator: Playwright locator object.

        Returns:
            list[list[str]]: List of text lines for each element.
        """
        feed_information = []
        for i in range(locator.count()):
            feed_information.append(locator.nth(i).inner_text().split("\n"))
        return feed_information

    def get_appraisal_settings(self):
        """
        Retrieve appraisal settings from the page.

        Returns:
            list[list[str]]: Appraisal settings items.
        """
        self.basicinfo.wait_for(state="visible")
        settings = self.basicinfo.locator("ul.listWrapper").locator(".mobSetting")
        return self.listgatherer(settings)

    def get_stackholders(self):
        """
        Retrieve stakeholder details.

        Returns:
            list[list[str]]: Stakeholder information.
        """
        self.basicinfo.wait_for(state="visible")
        users = self.basicinfo.locator("ul.listWrapper").locator(".userWrapper")
        return self.listgatherer(users)

    def get_associate_details(self):
        """
        Extract associate details such as name, employee ID, and role.

        Returns:
            tuple[str, str, str]: (Name, Employee ID, Role)
        """
        self.associate.wait_for(state="attached", timeout=5000)
        details = self.associate.inner_text().split("\n")
        name = details[0].split(", ")[1]
        empid = details[1].split(" | ")[0]
        role = details[1].split(" | ")[1]
        return name, empid, role

    def start_conversation(self):
        """
        Start or view the appraisal conversation and extract feedforward cards.

        Returns:
            dict: Feedforward card details grouped by section.
        """
        if self.conversation.is_visible():
            self.conversation.click()
        elif self.view_conversation.is_visible():
            self.view_conversation.click()

        self.page.get_by_role("button", name="Expand All").click()
        feedforward_cards = defaultdict(list)

        for card in range(self.cards.count()):
            inner_cards = self.cards.nth(card).locator("div.card")
            for inner_card in range(inner_cards.count()):
                card_title = inner_cards.nth(inner_card).locator("div.card-body.exp").inner_text()
                card_value = inner_cards.nth(inner_card).locator("span.sqa").inner_text()
                card_description = inner_cards.nth(inner_card).locator("p.praspc").inner_text()

                feedforward_cards[self.cards.nth(card).locator("h6").inner_text()].append({
                    "CardTitle": card_title.split("\n")[0].strip(),
                    "CardValue": "✓" if card_value.strip() == "" else card_value.strip(),
                    "CardDescription": card_description.strip(),
                })

        return dict(feedforward_cards)

    def feedback_fetcher(self, feedbackcards):
        """
        Extract details from feedback cards including attributes and previous messages.

        Args:
            feedbackcards: Playwright locator for feedback cards.

        Returns:
            list[dict]: List of feedback card details.
        """
        card_details = []
        for card in range(feedbackcards.count()):
            card_detail = {
                "cardNo": card,
                "cardHeading": feedbackcards.nth(card).locator("div.attributeHeading").inner_text(),
                "cardText": feedbackcards.nth(card).locator("div.attributeText").inner_text(),
                "previousmessages": [],
                "cardattributes": {},
            }

            # Handle previous messages
            conversation_wrapper = feedbackcards.nth(card).locator(".showConversationText")
            if conversation_wrapper.is_visible():
                conversation_wrapper.click()
                previous_comments = feedbackcards.nth(card).locator("ul.commentsList")
                for comment in range(previous_comments.count()):
                    message_wrapper = previous_comments.nth(comment).locator(".messageListWrapper")
                    for message in range(message_wrapper.count()):
                        message_content = message_wrapper.nth(message).locator("div.messageDetailsWrapper").inner_text()
                        message_details = {
                            "messageBy": message_content.split("\n")[0],
                            "messageBody": message_content.split("\n")[1] if len(message_content.split("\n")) > 1 else "",
                        }
                        card_detail["previousmessages"].append(message_details)
            else:
                message_wrapper = feedbackcards.nth(card).locator(".messageListWrapper")
                if message_wrapper.is_visible():
                    message_content = message_wrapper.locator("div.messageDetailsWrapper").inner_text()
                    message_details = {
                        "messageBy": message_content.split("\n")[0],
                        "messageBody": message_content.split("\n")[1] if len(message_content.split("\n")) > 1 else "",
                    }
                    card_detail["previousmessages"].append(message_details)
                else:
                    card_detail["previousmessages"].append({"messageBy": None, "messageBody": None})

            # Handle attributes
            attributes = feedbackcards.nth(card).locator("div.attributesListWrapper").locator("li")
            for attribute in range(attributes.count()):
                attribute_list = attributes.nth(attribute).inner_text().split("\n")
                if len(attribute_list) == 2:
                    card_detail["cardattributes"][attribute_list[0]] = attribute_list[1]
                else:
                    card_detail["cardattributes"][attribute_list[1]] = attribute_list[2]

            card_details.append(card_detail)

        return card_details

    def year_navigation(self):
        """
        Navigate to the latest appraisal year.
        """
        self.page.locator("div.ng-select-container").click()
        appraisal_years = self.page.locator("div.ng-dropdown-panel-items.scroll-host").inner_text().split("\n")
        year = appraisal_years[0]
        print(f"📅 Getting details for appraisal year: {year}")
        self.page.get_by_role("option", name="-" + year.split("-")[1]).click()

    def tab_clicker(self, tab):
        """
        Click on a specific tab and wait for content to load.

        Args:
            tab (str): Tab name to click.
        """
        self.tabs.get_by_text(tab).click()
        self.page.locator("div.infoWrapper").wait_for(state="visible")

    def get_goals(self):
        """
        Retrieve goal-related feedback cards.

        Returns:
            list[dict]: Goal card details.
        """
        self.tab_clicker("Goal(s)")
        return self.feedback_fetcher(self.feedbackcards)

    def get_attributes(self):
        """
        Retrieve attribute-related feedback cards.

        Returns:
            list[dict]: Attribute card details.
        """
        self.tab_clicker("Attribute(s)")
        return self.feedback_fetcher(self.feedbackcards)

    def feedback_filler(self, feedbackcards, content):
        """
        Fill feedback comments into the corresponding cards.

        Args:
            feedbackcards: Playwright locator for feedback cards.
            content (list[dict]): List of comments mapped to card numbers.
        """
        for card in range(feedbackcards.count()):
            for cardcontent in content:
                if cardcontent["cardNo"] == card:
                    feedbackcards.nth(card).get_by_role("textbox").fill(cardcontent["cardComment"]["comment"])
        self.page.pause()

    def fill_comments(self, tab, content):
        """
        Fill comments into goals or attributes based on tab selection.

        Args:
            tab (str): Either "Goals" or "Attributes".
            content (list[dict]): Comments to fill.
        """
        self.tab_clicker(tab)
        self.feedback_filler(self.feedbackcards, content)
