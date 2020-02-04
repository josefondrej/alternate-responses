import json
import os

import requests
from tqdm import tqdm

from randomization_without_garbage.randomization_suggestion import RandomizationSuggestion
from randomization_without_garbage.randomization_suggestion_pool import RandomizationSuggestionPool

DEFAULT_URL = "https://api.us-south.assistant.dev.watson.cloud.ibm.com"
DEFAULT_VERSION = "2019-02-28"


def get_response(utterance: str, skill_id: str, api_key: str, url: str = DEFAULT_URL, version: str = DEFAULT_VERSION):
    headers = {
        'Content-Type': 'application/json',
    }

    params = (
        ('version', version),
    )

    data = '{"input": {"text": "' + utterance + '"}, "alternate_intents": true}'

    response = requests.post(
        f"{url}/v1/workspaces/{skill_id}/message",
        headers=headers, params=params, data=data, auth=("apikey", api_key))

    return json.loads(str(response.content, "utf-8"))


def get_suggestion_pool(utterance: str, skill_id: str, api_key: str):
    response = get_response(utterance, skill_id, api_key)
    intents = response["intents"]
    suggestion_list = [RandomizationSuggestion(intent["intent"], intent["confidence"]) for intent in intents]
    return RandomizationSuggestionPool(suggestion_list)


if __name__ == "__main__":
    skill_ids = os.listdir("utterances")
    skill_ids = [skill_id.split(".")[0] for skill_id in skill_ids]

    with open("workspace_credentials.json", "r") as file:
        credentials = json.load(file)

    for skill_id in skill_ids:
        with open(f"utterances/{skill_id}.json", "r") as file:
            utterances = json.load(file)["utterances"]

        skill_credentials = credentials[skill_id]

        utterance_to_intents = dict()

        for utterance in tqdm(utterances):
            try:
                response = get_response(utterance, skill_credentials["skill_id"], skill_credentials["api_key"])
                intents = response["intents"]
                utterance_to_intents[utterance] = intents
            except Exception as e:
                print(f"[ERROR] {str(e)}")

        with open(f"utterances_to_intents/{skill_id}.json", "w") as file:
            json.dump(utterance_to_intents, file)
