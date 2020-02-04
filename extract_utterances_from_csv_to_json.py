import json
import os
from typing import List

import pandas as pd


def get_utterances(workspace_id) -> List[str]:
    utterance_csv = f"utterances/{workspace_id}.csv"
    utterance_dataframe = pd.read_csv(utterance_csv)
    utterances = list(utterance_dataframe["input text"])
    return utterances


if __name__ == "__main__":
    workspace_ids = os.listdir("utterances/")
    workspace_ids = [workspace_id.split(".")[0] for workspace_id in workspace_ids]
    for workspace_id in workspace_ids:
        utterances = get_utterances(workspace_id)

        out_file_path = f"utterances/{workspace_id}.json"
        with open(out_file_path, "w") as file:
            json.dump({"utterances": utterances}, file)
