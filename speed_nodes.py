"""
Automation pipeline for processing YAML appraisal data, generating comments via LLM,
and writing results back to disk.
"""

import yaml
from utils import call_llm
from pocketflow import Node, BatchNode, Flow


class DataGatherer(BatchNode):
    """
    Collect appraisal YAML files and store them in shared space as JSON-like structures.
    """

    def prep(self, shared):
        """
        Check if there is already any content in the shared storage.

        Args:
            shared (dict): Shared dictionary used across pipeline nodes.

        Returns:
            list[str]: List of filenames to process.
        """
        return shared.get(
            "files", ["Goals", "Attributes", "Settings", "feed_forward", "users_dict"]
        )

    def exec(self, prep_res):
        """
        Read required YAML file and prepare for storage.

        Args:
            prep_res (str): Filename stem (without extension).

        Returns:
            dict: Parsed YAML content.
        """
        with open(
            f"ContinousFeedback/details/{prep_res}.yaml", "r", encoding="UTF-8"
        ) as file:
            data = yaml.safe_load(file.read())
        # print(data)
        return data

    def post(self, shared, prep_res, exec_res):
        """
        Store the results into categorized shared keys.

        Args:
            shared (dict): Shared dictionary.
            prep_res (str): Filename stem.
            exec_res (dict): Parsed YAML content.

        Returns:
            str: Status string.
        """
        shared["speed_files"] = []
        shared["user_files"] = []
        for item in exec_res:
            item_key = list(item.keys())[0]
            if item_key in ["Goal(s)", "Attribute(s)"]:
                shared["speed_files"].append(item)
            elif item_key == "FeedForward":
                shared["user_files"] = item
            else:
                shared["misc_files"] = item
        return "default"


class CommentsGenerator(BatchNode):
    """
    Use LLM to generate concise appraisal comments for goals and attributes.
    """

    def prep(self, shared):
        """
        Prepare data for comment generation.

        Args:
            shared (dict): Shared dictionary.

        Returns:
            list[dict]: Speed files containing goals/attributes.
        """
        return shared["speed_files"]

    def exec(self, prep_res):
        """
        Generate comments for each goal/attribute using LLM.

        Args:
            prep_res (dict): Parsed YAML content for a single category.

        Returns:
            dict: Updated content with generated comments.
        """
        key_name = list(prep_res.keys())[0]
        with open(
            "./ContinousFeedback/details/feed_forward.yaml", "r", encoding="UTF-8"
        ) as f:
            feed_forward = f.read()

        with open(
            "./ContinousFeedback/details/user_comments.txt", "r", encoding="UTF-8"
        ) as f:
            user_comments = f.read()

        for index, item in enumerate(prep_res[key_name]):
            print(f"📝 Generating comments for {key_name} {index + 1}...")
            prompt = f"""
# CONTEXT
You are assisting a top-performing employee in drafting comments for their annual goal sheet.

**Topic:** {item['cardHeading']}
**Manager Requirement:** {item['cardText']}
**Previous Conversation (from Associate's Perspective):** {yaml.dump(item["previousmessages"], sort_keys=False)}
**User Details Context:** {yaml.safe_load(feed_forward)}
**User Comments:** {user_comments}

# ACTION
Generate the content in yaml format, as defined below:
```yaml
comment: Draft a concise, positive one-liner comment.
reason: What is the information used for the content
```

# RESULT
The response must emphasize the employee's performance and achievements in a natural, conversational style.
The comment should feel like a continuation of the previous conversation, showing awareness of what was already said.

# STYLE
1. Write in the first person, reflecting the associate's voice—modest yet affirming of their accomplishments.
2. Prioritize alignment with the manager's requirements, but let the previous conversation guide tone and focus.
3. Maintain a positive, supportive tone.
4. Be concise and avoid over-advertising the associate's achievements.
5. If something is unclear, lean on the context of prior messages rather than inventing new details.

# NOTE
Never, ever go overboard with the comments and always stick to the point of topic only.
Use only the relevant information from the user Comments... If it is not relevant, do not take it into consideration.
Do not use any Unicode characters.
Some details may be incomplete or ambiguous—use the previous conversation to fill gaps naturally.
Do not assume any thing, be sure to ask for any additional information needed, so that the associate can provide more factual information
"""
            content = call_llm(prompt).replace("’", "'")
            stripped_content = content.split("```yaml")[1].split("```")[0].strip()
            structured_result = yaml.safe_load(stripped_content)
            assert "comment" in structured_result, "Comment is mandatory"
            item["cardComment"] = structured_result
        return prep_res

    def post(self, shared, prep_res, exec_res):
        """
        Store generated comments in shared dictionary.

        Args:
            shared (dict): Shared dictionary.
            prep_res (dict): Input data.
            exec_res (dict): Data with generated comments.
        """
        shared["FinalComments"] = exec_res


class CommentFinalizer(BatchNode):
    """
    Proofread the genereated comments
    """

    def prep(self, shared):
        return shared["FinalComments"]

    def exec(self, prep_res):
        key_name = list(prep_res.keys())[0]
        for index, item in enumerate(prep_res[key_name]):
            print(f"📝 Finishing up comments for {key_name} {index + 1}...")
            prompt = f"""
# CONTEXT
Given the context for Topic, Requirement, Previous messages and User Comment.
Your job is to ensure the comments are fully aligned with the everything above.

**Topic:** {item['cardHeading']}
**Manager Requirement:** {item['cardText']}
**Previous Conversation (from Associate's Perspective):** {yaml.dump(item["previousmessages"], sort_keys=False)}
**Comment:** {item['cardComment']}

# ACTION
If there is any conversation that already exists and if the latest comment is from the user.
    There should ONLY be any empty comment. This will ensure there is no repeation of associate message.
The output should be in yaml format, as shown below
```yaml
original_comment: # This is the original comment
comment_changed: true | false
reason_for_change: <reason to justify the changed>
suggested_comment: <populate only if there is a change what should be the changed comment>
```
            """
            print(call_llm(prompt))

    def post(self, shared, prep_res, exec_res): ...


class OutputFileWriter(Node):
    """
    Write final generated comments to a YAML file.
    """

    def prep(self, shared):
        """
        Fetch the necessary object from shared dictionary.

        Args:
            shared (dict): Shared dictionary.

        Returns:
            dict: Final comments.
        """
        return shared["FinalComments"]

    def exec(self, prep_res):
        """
        Write generated comments to disk.

        Args:
            prep_res (dict): Final comments data.
        """
        with open(
            "ContinousFeedback/details/final_comments.yaml", "w", encoding="UTF-8"
        ) as file:
            file.write(yaml.dump(prep_res, sort_keys=False, line_break="\n"))


if __name__ == "__main__":
    shared_dict = {}  # Initialize shared dictionary
    gatherer = DataGatherer()
    comments = CommentsGenerator()
    finalizer = CommentFinalizer()
    writer = OutputFileWriter()

    # Define pipeline
    gatherer >> comments >> finalizer >> writer

    flow = Flow(gatherer)
    flow.run(shared_dict)
    # print(shared_dict)
