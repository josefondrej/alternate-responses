## # ################################################################## #
## #                                                                    #
## # IBM Confidential                                                   #
## # OCO Source Materials                                               #
## #                                                                    #
## # (C) Copyright IBM Corp. 2018, 2018                                 #
## #                                                                    #
## # The source code for this program is not published or otherwise     #
## # divested of its trade secrets, irrespective of what has been       #
## # deposited with the U.S. Copyright Office.                          #
## #                                                                    #
## # ################################################################## #
from typing import List

from randomization_without_garbage.randomization_suggestion import RandomizationSuggestion


class RandomizationSuggestionPool(object):
    def __init__(self, suggestions: List[RandomizationSuggestion]):
        self._suggestions = suggestions

    @property
    def visible_suggestions(self):
        return [suggestion for suggestion in self.suggestions if suggestion.is_visible]

    @property
    def sorted_suggestions(self):
        sorted_suggestions = list(self.suggestions)
        sorted_suggestions.sort(key=lambda suggestion: suggestion.score, reverse=True)
        return sorted_suggestions

    @property
    def sorted_visible_suggestions(self):
        return [suggestion for suggestion in self.sorted_suggestions if suggestion.is_visible]

    @property
    def suggestions(self) -> List[RandomizationSuggestion]:
        return self._suggestions

    @property
    def scores(self) -> List[float]:
        return [suggestion.score for suggestion in self.suggestions]

    @property
    def names(self) -> List[str]:
        return [suggestion.name for suggestion in self.suggestions]

    @property
    def are_visible(self) -> List[bool]:
        return [suggestion.is_visible for suggestion in self.suggestions]

    @property
    def visible_scores(self) -> List[float]:
        return [suggestion.score for suggestion in self.suggestions if suggestion.is_visible]

    @property
    def visible_names(self) -> List[str]:
        return [suggestion.name for suggestion in self.suggestions if suggestion.is_visible]

    @property
    def top_visible_suggestion(self) -> RandomizationSuggestion:
        return self.sorted_visible_suggestions[0] if self.sorted_visible_suggestions else None

    @property
    def top_suggestion(self):
        return self.sorted_suggestions[0] if self.sorted_suggestions else None

    @property
    def visible_count(self):
        return len(self.visible_suggestions)

    @property
    def suggestion_count(self):
        return len(self.suggestions)

    @property
    def sorted_visible_scores(self):
        return [suggestion.score for suggestion in self.sorted_visible_suggestions]

    @property
    def top_visible_suggestion_after_the_top_suggestion(self):
        if not self.top_suggestion.is_visible:
            return self.visible_suggestions[0]
        else:
            return self.visible_suggestions[1]

    def is_top_suggestion(self, suggestion: RandomizationSuggestion) -> bool:
        return self.sorted_suggestions[0] == suggestion

    def set_scores(self, scores: List[float]):
        if len(scores) != self.suggestion_count:
            raise AssertionError(f"Mismatch between lenght of scores ({len(scores)}) "
                                 f"and number of suggestions in pool ({self.suggestion_count})")
        for suggestion, score in zip(self._suggestions, scores):
            suggestion._score = score

    @property
    def normalized_suggestion_scores(self):
        max_score = max(1, self.top_suggestion.score)
        return [suggestion.score / max_score for suggestion in self.suggestions]

    @property
    def normalized_visible_suggestion_scores(self):
        max_score = max(1, self.top_visible_suggestion.score)
        return [suggestion.score / max_score for suggestion in self.visible_suggestions]

    @property
    def visible_pool(self):
        return RandomizationSuggestionPool(self.visible_suggestions)

    def clone(self):
        suggestions = [suggestion.clone() for suggestion in self.suggestions]
        return RandomizationSuggestionPool(suggestions)

    @property
    def is_empty(self) -> bool:
        return len(self.suggestions) == 0

    @property
    def propensities(self) -> List[float]:
        return [suggestion.propensity for suggestion in self.suggestions]

    def find_sample(self, sample: List[RandomizationSuggestion]) -> List[RandomizationSuggestion]:
        suggestion_lookup_dict = {original_suggestion.name: original_suggestion
                                  for original_suggestion in self.suggestions}
        original_sample = [suggestion_lookup_dict[suggestion.name] for suggestion in sample]
        return original_sample

    def get_original_order(self, shuffled_pool: "RandomizationSuggestionPool") -> List[int]:
        name_to_original_index = {suggestion.name: index for index, suggestion in enumerate(self.suggestions)}
        return [name_to_original_index[suggestion.name] for suggestion in shuffled_pool.suggestions]
