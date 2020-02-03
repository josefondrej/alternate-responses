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
class RandomizationSuggestion(object):
    def __init__(self, name: str, score: float, is_visible: bool = True, propensity: float = None):
        self._name = name
        self._score = score
        self._is_visible = is_visible
        self._propensity = propensity

    def __eq__(self, other):
        return isinstance(other, RandomizationSuggestion) and \
               other.name == self.name and \
               other.score == self.score and \
               other.is_visible == self.is_visible

    def __hash__(self):
        return hash((self._name, self._score, self._is_visible))

    @property
    def name(self):
        return self._name

    @property
    def score(self):
        return self._score

    @property
    def is_visible(self):
        return self._is_visible

    @property
    def propensity(self):
        return self._propensity

    def clone(self):
        return RandomizationSuggestion(name=self.name, score=self.score, is_visible=self.is_visible)
