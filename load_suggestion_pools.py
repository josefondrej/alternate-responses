import json

from randomization_without_garbage.randomization_suggestion import RandomizationSuggestion
from randomization_without_garbage.randomization_suggestion_pool import RandomizationSuggestionPool


def get_utterance_to_suggestion_pool(data_path: str):
    with open(data_path, "r") as file:
        data = json.load(file)

    utterance_to_suggestion_pool = dict()

    for utterance, utterance_intents in data.items():
        suggestions = [RandomizationSuggestion(name=intent["intent"], score=intent["confidence"]) for intent in
                       utterance_intents]
        suggestion_pool = RandomizationSuggestionPool(suggestions)
        utterance_to_suggestion_pool[utterance] = suggestion_pool

    return utterance_to_suggestion_pool


if __name__ == "__main__":
    data_path = "utterance_to_intents.json"

    utterance_to_suggestion_pool = get_utterance_to_suggestion_pool(data_path)
    print(utterance_to_suggestion_pool["leave"].scores)
