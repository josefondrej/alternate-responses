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
import random
from typing import List, Dict, Any

import numpy as np
from scipy import stats

from randomization_without_garbage.randomization_suggestion import RandomizationSuggestion
from randomization_without_garbage.randomization_suggestion_pool import RandomizationSuggestionPool


class SuggestionSamplerV3(object):
    def __init__(self,
                 min_suggestion_count: int,
                 max_suggestion_count: int,
                 disambiguation_percentage_parameter: float,
                 disambiguation_length_parameter: float,
                 first_suggestion_boost_parameter: float,
                 first_suggestion_top_position_boost_parameter: float,
                 disambiguation_percentage_parameter_sample_size: float,
                 min_suggestion_score: float):

        super().__init__()
        self._min_suggestion_count = min_suggestion_count
        self._max_suggestion_count = max_suggestion_count
        self._disambiguation_percentage_parameter = disambiguation_percentage_parameter
        self._disambiguation_length_parameter = disambiguation_length_parameter
        self._first_suggestion_boost_parameter = first_suggestion_boost_parameter
        self._first_suggestion_top_position_boost_parameter = first_suggestion_top_position_boost_parameter

        # Do not play with these defaults unless you really know what you're doing
        self._disambiguation_percentage_parameter_sample_size = disambiguation_percentage_parameter_sample_size
        self._min_suggestion_score = min_suggestion_score

    def sample(self, suggestion_pool: RandomizationSuggestionPool) -> List[RandomizationSuggestion]:
        suggestion_pool_clone = self._get_preprocessed_pool(suggestion_pool)
        if suggestion_pool_clone.is_empty:
            sample = []
        else:
            disambiguate = self._sample_disambiguate(suggestion_pool_clone)
            if not disambiguate:
                sample = [suggestion_pool_clone.top_suggestion]
            else:
                disambiguation_length = self._sample_disambiguation_length(suggestion_pool_clone)
                sample = self._sample_n(suggestion_pool_clone, disambiguation_length)

        original_sample = suggestion_pool.find_sample(sample)
        self._boost_first_suggestion_to_the_top(original_sample, suggestion_pool.top_suggestion)
        return original_sample

    def calculate_propensities(self, suggestion_pool: RandomizationSuggestionPool) -> List[float]:
        suggestion_pool_clone = self._get_preprocessed_pool(suggestion_pool)
        propensities = []
        if suggestion_pool_clone.is_empty:
            pass
        else:
            pdf_disambiguation = self._pdf_disambiguate(suggestion_pool_clone)
            pdf_disambiguation_length = self._pdf_disambiguation_length(suggestion_pool_clone)

            for suggestion in suggestion_pool_clone.suggestions:
                suggestion_propensity = 0.
                for disambiguation_length in list(pdf_disambiguation_length.keys()):
                    suggestion_propensity += pdf_disambiguation_length[disambiguation_length] * \
                                             self._propensity_n(suggestion, suggestion_pool_clone,
                                                                disambiguation_length)

                suggestion_propensity *= pdf_disambiguation[True]
                if suggestion_pool_clone.is_top_suggestion(suggestion):
                    suggestion_propensity += pdf_disambiguation[False]

                propensities.append(suggestion_propensity)

        original_suggestion_order = suggestion_pool.get_original_order(suggestion_pool_clone)
        return [propensities[i] for i in original_suggestion_order]

    def _boost_first_suggestion_to_the_top(self, sample: List[RandomizationSuggestion],
                                           top_suggestion: RandomizationSuggestion):
        if top_suggestion in sample:
            r = random.random()
            if r < self._first_suggestion_top_position_boost_parameter:
                sample.insert(0, sample.pop(sample.index(top_suggestion)))

    def _sample_n(self, suggestion_pool: RandomizationSuggestionPool, n: int) -> List[RandomizationSuggestion]:
        single_draw_probas = self._get_skewed_probabilities(suggestion_pool)
        sample_indices = []
        for i in range(n):
            sampled_index = self._sample_key(single_draw_probas)
            sample_indices.append(sampled_index)
            single_draw_probas.pop(sampled_index)

        sampled_suggestions = [suggestion_pool.suggestions[index] for index in sample_indices]
        return sampled_suggestions

    def _propensity_n(self, suggestion: RandomizationSuggestion, suggestion_pool: RandomizationSuggestionPool,
                      n: int) -> float:
        single_draw_probas = self._get_skewed_probabilities(suggestion_pool)
        for suggestion_index, orig_suggestion in enumerate(suggestion_pool.suggestions):
            if suggestion == orig_suggestion:
                break

        return 1. - self._proba_index_not_in_sample_of_size_n(suggestion_index, single_draw_probas, n)

    def _proba_index_not_in_sample_of_size_n(self, index: int, single_draw_probas: Dict[int, float], n: int) -> float:
        p_index = single_draw_probas[index]
        if p_index == 0:
            return 1.

        if n == 1:
            return 1. - p_index

        proba_index_not_in_sample = 0
        for i, p in single_draw_probas.items():
            if i == index:
                continue

            new_single_draw_probas = dict(single_draw_probas)
            new_single_draw_probas.pop(i)
            new_single_draw_probas = {k: v / (1 - p) for k, v in new_single_draw_probas.items()}
            proba_index_not_in_sample += p * self._proba_index_not_in_sample_of_size_n(index,
                                                                                       new_single_draw_probas,
                                                                                       n - 1)
        return proba_index_not_in_sample

    def _proba_item_not_in_sample_of_size_n(self, item_proba: float, other_single_draw_probas: List[float], n: int):
        if item_proba == 0:
            return 1.

        if n == 1:
            return 1. - item_proba

        proba_item_not_in_sample = 0.
        for i in range(len(other_single_draw_probas)):
            selected_proba = other_single_draw_probas[i]
            new_item_proba = item_proba / (1 - selected_proba)
            new_other_single_draw_probas = [p / (1 - selected_proba) for p_index, p in
                                            enumerate(other_single_draw_probas) if
                                            p_index != i]
            proba_item_not_in_sample += selected_proba * self._proba_item_not_in_sample_of_size_n(new_item_proba,
                                                                                                  new_other_single_draw_probas,
                                                                                                  n - 1)
            return proba_item_not_in_sample

    def _get_skewed_probabilities(self, suggestion_pool: RandomizationSuggestionPool) -> Dict[int, float]:
        scores = np.array(
            [suggestion.score if suggestion.is_visible else 0.0 for suggestion in suggestion_pool.suggestions])
        normalized_scores = scores / max(scores)
        skewed_scores = normalized_scores ** self._first_suggestion_boost_parameter
        skewed_probabilities = skewed_scores / sum(skewed_scores)
        return {i: proba for i, proba in enumerate(skewed_probabilities)}

    def _get_preprocessed_pool(self, suggestion_pool: RandomizationSuggestionPool) -> RandomizationSuggestionPool:
        cloned_pool = suggestion_pool.clone()
        cloned_pool._suggestions.sort(key=lambda sug: -sug.score)
        new_scores = [max(self._min_suggestion_score, suggestion.score) for suggestion in cloned_pool.suggestions]
        cloned_pool.set_scores(new_scores)
        return cloned_pool

    def _pdf_disambiguation_length(self, suggestion_pool: RandomizationSuggestionPool) -> Dict[int, float]:
        """ Probability distribution function of sample length """
        pdf = {}
        min_length = self._min_suggestion_count
        max_length = min(self._max_suggestion_count, suggestion_pool.visible_count)
        if max_length < min_length:
            return {}
        probabilities = np.array(suggestion_pool.normalized_visible_suggestion_scores)[min_length:max_length]
        probabilities = np.minimum(1, probabilities * self._disambiguation_length_parameter)

        for n in range(0, max_length - min_length + 1):
            mass = self._probability_choose_n(probabilities, n)
            pdf[n + min_length] = mass

        return pdf

    def _probability_choose_n(self, probabilities_choose_one: List[float], n: int) -> float:
        m = len(probabilities_choose_one)
        proba_exactly_n_selected_from_probas_up_to_m = [[0 for j in range(n + 2)] for i in range(m + 1)]
        proba_exactly_n_selected_from_probas_up_to_m[0][1] = 1.

        for i in range(1, m + 1):
            for j in range(1, n + 2):
                p = probabilities_choose_one[i - 1]
                left_top = proba_exactly_n_selected_from_probas_up_to_m[i - 1][j - 1]
                top = proba_exactly_n_selected_from_probas_up_to_m[i - 1][j]
                proba_exactly_n_selected_from_probas_up_to_m[i][j] = p * left_top + (1 - p) * top

        return proba_exactly_n_selected_from_probas_up_to_m[m][n + 1]

    def _pdf_disambiguate(self, suggestion_pool: RandomizationSuggestionPool) -> Dict[bool, float]:
        if suggestion_pool.visible_count < self._min_suggestion_count:
            probability_disambiguation_occurs = 0.
        else:
            c1 = suggestion_pool.top_suggestion.score
            c2 = suggestion_pool.top_visible_suggestion_after_the_top_suggestion.score
            certainty_ratio = c2 / c1
            alpha = self._disambiguation_percentage_parameter * self._disambiguation_percentage_parameter_sample_size
            beta = (1 - self._disambiguation_percentage_parameter) * \
                   self._disambiguation_percentage_parameter_sample_size
            probability_disambiguation_occurs = stats.beta.cdf(certainty_ratio, alpha, beta)

        return {True: probability_disambiguation_occurs, False: 1 - probability_disambiguation_occurs}

    def _sample_disambiguation_length(self, suggestion_pool: RandomizationSuggestionPool) -> int:
        pdf = self._pdf_disambiguation_length(suggestion_pool)
        return self._sample_key(pdf)

    def _sample_disambiguate(self, suggestion_pool: RandomizationSuggestionPool) -> bool:
        pdf = self._pdf_disambiguate(suggestion_pool)
        return self._sample_key(pdf)

    def _sample_key(self, pdf: Dict[Any, float]) -> Any:
        keys = []
        values = []
        for k, v in pdf.items():
            keys.append(k)
            values.append(v)

        probas = list(values)
        probas = [p / sum(probas) for p in probas]
        r = random.random()

        for key_index in range(0, len(keys)):
            if sum(probas[:(key_index + 1)]) >= r:
                break

        return keys[key_index]
