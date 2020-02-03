from randomization_without_garbage.suggestion_sampler_v3 import SuggestionSamplerV3
from sampler_kwargs import default, dialog_alternate_responses


def get_sampler(type: str = "default"):
    type_to_sampler_kwargs = {
        "default": default,
        "alternate": dialog_alternate_responses}

    sampler_kwargs = type_to_sampler_kwargs[type]
    sampler = SuggestionSamplerV3(**sampler_kwargs)
    return sampler
