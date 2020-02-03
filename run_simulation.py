from typing import List, Dict

import numpy as np
import matplotlib.pyplot as plt

from get_sampler import get_sampler
from load_suggestion_pools import get_utterance_to_suggestion_pool
from randomization_without_garbage.randomization_suggestion_pool import RandomizationSuggestionPool


class AssistantResponse(object):
    def __init__(self, disambiguation_triggered: bool, disambiguation_length: int,
                 alternate_responses_triggered: bool, alternate_responses_length: int):
        self.disambiguation_triggered = disambiguation_triggered
        self.disambiguation_length = disambiguation_length
        self.alternate_responses_triggered = alternate_responses_triggered
        self.alternate_responses_length = alternate_responses_length


def get_disambiguation_proba(responses: List[AssistantResponse]):
    proba = np.mean(1 * [response.disambiguation_triggered for response in responses])
    return proba


def get_disambiguation_len(responses: List[AssistantResponse]):
    length = np.mean([response.disambiguation_length for response in responses])
    return length


def get_alternate_proba(responses: List[AssistantResponse]):
    proba = np.mean(1 * [response.alternate_responses_triggered for response in responses])
    return proba


def get_alternate_len(responses: List[AssistantResponse]):
    length = np.mean([response.alternate_responses_length for response in responses])
    return length


def barplot_dict(title: str, dictionary: Dict, color: str = "deepskyblue"):
    keys = list(dictionary.keys())
    values = [dictionary[k] for k in keys]
    x = range(len(keys))

    plt.title(title)
    plt.bar(x, values, align='center', color=color)
    plt.xticks(x, keys, rotation=90)
    plt.show()


def sample_responses(utterance_to_suggestion_pool: Dict[str, RandomizationSuggestionPool], sample_count: int = 1000):
    default_sampler = get_sampler("default")
    alternate_sampler = get_sampler("alternate")

    utterance_to_responses: Dict[str, List[AssistantResponse]] = dict()

    for utterance, utterance_suggestion_pool in utterance_to_suggestion_pool.items():
        assistant_outcomes = []

        for i in range(sample_count):
            sampled_suggestions = default_sampler.sample(utterance_suggestion_pool)
            sampled_suggestions_names = [suggestion.name for suggestion in sampled_suggestions]
            remaining_suggestions = [suggestion for suggestion in utterance_suggestion_pool.suggestions
                                     if suggestion.name not in sampled_suggestions_names]
            remaining_pool = RandomizationSuggestionPool(remaining_suggestions)
            alternate_suggestions = alternate_sampler.sample(remaining_pool)

            disambiguation_triggered = len(sampled_suggestions) > 1
            disambiguation_length = len(sampled_suggestions)
            alternate_responses_triggered = len(alternate_suggestions) > 1
            alternate_responses_length = len(alternate_suggestions)

            assistant_response = AssistantResponse(disambiguation_triggered, disambiguation_length,
                                                   alternate_responses_triggered, alternate_responses_length)
            assistant_outcomes.append(assistant_response)

        utterance_to_responses[utterance] = assistant_outcomes
    return utterance_to_responses


def plot_response_statistics(utterance_to_responses: Dict[str, List[AssistantResponse]]):
    disambiguation_probas = {utterance: get_disambiguation_proba(responses)
                             for utterance, responses in utterance_to_responses.items()}
    disambiguation_lens = {utterance: get_disambiguation_len(responses)
                           for utterance, responses in utterance_to_responses.items()}
    alternate_probas = {utterance: get_alternate_proba(responses)
                        for utterance, responses in utterance_to_responses.items()}
    alternate_lens = {utterance: get_alternate_len(responses)
                      for utterance, responses in utterance_to_responses.items()}

    barplot_dict("Disambiguation probability", disambiguation_probas)
    barplot_dict("Disambiguation length", disambiguation_lens, color="orange")
    barplot_dict("Alternate responses probability", alternate_probas)
    barplot_dict("Alternate responses length", alternate_lens, color="orange")


if __name__ == "__main__":
    data_path = "utterance_to_intents.json"

    utterance_to_suggestion_pool = get_utterance_to_suggestion_pool(data_path)

    utterance_to_responses = sample_responses(utterance_to_suggestion_pool, 100)

    plot_response_statistics(utterance_to_responses)
