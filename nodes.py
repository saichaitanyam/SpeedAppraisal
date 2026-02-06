"""_summary_"""

from pocketflow import Node, BatchNode, Flow
import yaml, json
from utils import call_llm

class DataGatherer(BatchNode):
    """"""
    def prep(self, shared):
        """Check if there is already any content in the Shared Storage"""
        return shared.get("files", ["Goal", "Attribute"])

    def exec(self, prep_res):
        """Read required files and prep for storage"""
        with open("ContinousFeedback/details/" + prep_res + ".yml", "r", encoding="UTF-8") as file:
            data = yaml.safe_load(file.read())
        return data

    def post(self, shared, prep_res, exec_res):
        """Store the results"""
        shared["speed_files"] = exec_res
        return "default"

class BatchProcessor(Node):
    """"""
    def prep(self, shared):
        """Read the list of files"""
        return shared["speed_files"]

    def exec(self, prep_res):
        """This will process"""
        # User just need to write for one element
        data_json = []
        for sp_items in prep_res:
            # print(sp_items)
            sp_keys = [i for i in sp_items.keys()]
            for sp_key in sp_keys:
                # print(sp_key)
                for index, value in enumerate(sp_items[sp_key]):
                    data_json.append({
                    sp_key + " " + str(index + 1): value,
                    "value": None
                    })
        return data_json

    def post(self, shared, prep_res, exec_res):
        """Store the correspoding comments into the shared dictionay"""
        shared["expanded_data"] = exec_res
        return "default"

class CommentsGenerator(BatchNode):
    """Use LLM to Generate Comments"""
    def prep(self, shared):
        return shared["expanded_data"]

    def exec(self, prep_res):
        key_name = list(prep_res)[0]
        prompt = f"""
        # CONTEXT
        You are assisting a modest, top-performing employee in drafting comments for their annual goal sheet.
        Manager Expectation: {prep_res[key_name]}
        Employee Input: {prep_res['value']}

        # ACTION
        Generate a concise, positive one-liner.

        # RESULT
        The response should highlight the employee's performance and achievements in a natural, user-written style.

        # STYLE
        Write in first person, as if the employee is speaking—modest in tone, but without downplaying their accomplishments.

        # NOTE
        Avoid using any Unicode characters.
        """
        prep_res["value"] = call_llm(prompt).replace("’","'")
        print(prep_res["value"])
        return prep_res

    def post(self, shared, prep_res, exec_res):
        shared["comments"] = exec_res

class Evaluator(Node):
    """Evaluate the results of LLM Output"""
    def prep(self, shared):
        """Fetch the necessary Object"""
        return shared["comments"]

    def exec(self, prep_res):
        """For each element in the genereated comments, evaluate if it is relevent"""
        with open("ContinousFeedback/" + "final_comments.yaml", "w", encoding="UTF-8") as file:
            file.write(yaml.dump(comments))

if __name__ == "__main__":
    shared_dict = {}  # Initialize shared dictionary
    gatherer = DataGatherer()
    processor = BatchProcessor()
    comments = CommentsGenerator()
    evaluator = Evaluator()

    gatherer >> processor >> comments >> evaluator

    flow = Flow(gatherer)
    flow.run(shared_dict)

