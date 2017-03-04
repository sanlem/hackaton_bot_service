import pickle
import logging


logger = logging.getLogger(__name__)


class SynonymDict:
    def __init__(self):
        self._dict = {}
        data = pickle.load(open('./utils/data/pickled_synonims.txt', 'rb'))
        for word, synonym in data.items():
            if synonym not in self._dict:
                self._dict[synonym] = word
                logger.debug("Added synonym pair '{}': '{}'.".format(synonym, word))

    def get_synonym(self, word):
        synonym = self._dict.get(word, None)
        if synonym is not None:
            logger.info("Found synonym '{}' for word '{}'.".format(synonym, word))
        else:
            logger.info("Found no synonym for word '{}'.".format(word))
        return synonym
