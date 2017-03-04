import logging
import pymorphy2
from gensim import corpora, models, similarities
from utils.synonimdict import SynonymDict


logger = logging.getLogger(__name__)
DATA_FOLDER = './bots/data/'


class ChatBot:
    SYNONYMS = SynonymDict()

    def __init__(self, name, data):
        self.name = name

        self.morph = pymorphy2.MorphAnalyzer()

        self.question_data_file_name = '{}faq_{}.data'.format(DATA_FOLDER,
                                                              self.name)
        self.faq_dict_file_name = '{}faq_{}.dict'.format(DATA_FOLDER, self.name)
        self.faq_corpus_file_name = '{}faq_{}.mm'.format(DATA_FOLDER, self.name)
        self.faq_lsi_file_name = '{}faq_{}.lsi'.format(DATA_FOLDER, self.name)
        self.faq_index_file_name = '{}faq_{}.index'.format(DATA_FOLDER, self.name)

        # self.is_ready = False

        try:
            self.faq_dictionary = corpora.Dictionary.load(self.faq_dict_file_name)
            self.faq_corpus = corpora.MmCorpus(self.faq_corpus_file_name)
            self.faq_lsi = models.LsiModel.load(self.faq_lsi_file_name)
            self.faq_index = similarities.MatrixSimilarity.load(self.faq_index_file_name)
        except FileNotFoundError:
            logger.info('Bot {} could not load its data.'.format(self.name))
            self.is_ready = False
            self.load_faq_data(data['faqs'])
        else:
            self.is_ready = True

    def load_faq_data(self, data):
        documents = list(data.keys())
        # dictionary = self.prepare_dictionary(documents)

        documents = [ChatBot.remove_crap(text) for text in documents if text]
        normalized = self.normalize_documents(documents, self.morph)
        self.faq_dictionary = corpora.Dictionary(normalized)
        self.faq_dictionary.save(self.faq_dict_file_name)

        faq_corpus = [self.faq_dictionary.doc2bow(doc) for doc in normalized]
        corpora.MmCorpus.serialize(self.faq_corpus_file_name, faq_corpus)
        self.faq_corpus = faq_corpus

        faq_tfidf = models.TfidfModel(self.faq_corpus)
        faq_corpus_tfidf = faq_tfidf[self.faq_corpus]
        faq_num_topics = len(normalized) // 2
        if faq_num_topics == 0:
            faq_num_topics = 1
        logger.info('Num of faq topics: {}'.format(faq_num_topics))
        self.faq_lsi = models.LsiModel(faq_corpus_tfidf, id2word=self.faq_dictionary,
                                       num_topics=faq_num_topics)
        self.faq_lsi.save(self.faq_lsi_file_name)

        # transform corpus to LSI space and index it
        faq_index = similarities.MatrixSimilarity(self.faq_lsi[self.faq_corpus])
        faq_index.save(self.faq_index_file_name)
        self.faq_index = faq_index

    @staticmethod
    def normalize_documents(documents, parser):
        """
        Normalizes texts: parses words to normal form and removes bad parts of speech.
        :param documents: list of strings
        :param parser: pymorphy2 MorphAnalyzer object
        :return: list of normalized documents.
        """
        def is_productive(word):
            """
            Check if word is productive part of speech.
            """
            return parser.parse(word)[0].tag.is_productive()

        def process_word(word):
            """
            Processes one portion of text. Parses word to normal form and replaces it with synonym.
            """
            word = parser.parse(word)[0].normal_form
            synonym = ChatBot.SYNONYMS.get_synonym(word)
            return synonym if synonym is not None else word

        new_docs = [[process_word(word) for word in document.lower().split() if is_productive(word)]
                    for document in documents]
        return new_docs

    @staticmethod
    def remove_crap(text):
        """
        Removes bad symbols from text.
        """
        new = str(text).lower()
        crap_symbols = '! . , : ; - ?'.split()
        for s in crap_symbols:
            if s in new:
                new = new.replace(s, '')
        return new

