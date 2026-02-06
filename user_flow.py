from speed_nodes import DataGatherer, CommentsGenerator, OutputFileWriter
from pocketflow import Flow


def create_flow(shared):
    shared_dict = {}  # Initialize shared dictionary
    gatherer = DataGatherer()
    comments = CommentsGenerator()
    writer = OutputFileWriter()

    gatherer >> comments >> writer

    flow = Flow(gatherer)
    flow.run(shared_dict)


if __name__ == "__main__":
    shared = {}  # Initialize shared dictionary
    create_flow(shared)
