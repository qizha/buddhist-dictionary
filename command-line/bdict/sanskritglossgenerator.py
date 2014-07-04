"""Module to generate output text with gloss from a Sanskrit text document. ===

The analysis is output in either HTML format with links back to the phrase 
memory and dictionary for each phrase and word in the Sanskrit text or POS tag 
format.
"""

import codecs
import os.path
import re

from datetime import date

from bdict import app_exceptions
from bdict import configmanager
from bdict import sanskritvocab

DEFAULT_OUTFILE_HTML = 'temp.html'
DEFAULT_OUTFILE_POS = 'temp.txt'


class GlossGenerator:
    """Generates a document annotated with English gloss and other information.
   """

    def __init__(self):
        """Constructor for GlossGenerator class.
        """
        manager = configmanager.ConfigurationManager()
        self.config = manager.LoadConfig()

    def GenerateDoc(self, corpus_entry):
        """Generates output text for the glossed version of the Chinese document.

        Args:
          corpus_entry: the corpus entry for the source document.

        Returns:
          A string with the generated output text.

        Raises:
          BDictException: If the input file does not exist
        """
        markup = ''
        if 'source_name' in corpus_entry:
            source_name = corpus_entry['source_name']
            markup += self._Title2(source_name)
        markup += self._Paragraph('Mouse over Sanskrit words for English gloss')
        if 'source_name' in corpus_entry:
            source = corpus_entry['source']
            markup += self._Paragraph('Source of document: %s' % source)
        if 'reference' in corpus_entry:
            reference = corpus_entry['reference']
            markup += self._Paragraph('Reference: %s\n' % reference)
        if 'plain_text' in corpus_entry:
            plain_text = corpus_entry['plain_text']
            # markup += self._Paragraph('Source document: %s' % plain_text)

        vocab = sanskritvocab.SanskritVocabulary()
        sdict = vocab.OpenDictionary()
        cdict = vocab.OpenCompoundsList()
        combined_dict = dict(sdict.items() + cdict.items())

        directory = self.config['corpus_directory']
        infile = corpus_entry['plain_text']
        fullpath = '%s/%s' % (directory, infile)
        with codecs.open(fullpath, 'r', "utf-8") as f:
            for line in f:
                if line.find('---END---') != -1:
                    break
                words = line.split()
                for token in words:
                    punc = None
                    element = sanskritvocab.ConvertNonStandard(token).strip()
                    if element.find('|') > 0:
                        (element, punc) = self._extractPunc(element)
                    if element in combined_dict:
                        print('element found: "%s"' % element)
                        entry = combined_dict[element]
                        entry_id = entry['id']
                        if 'no_parts' in entry: # Phrase
                            markup += self._Phrase(element, entry)
                        else: # Word
                            markup += self._Word(element, entry)
                    else:
                        print('element not found: "%s"' % element)
                        markup += self._Punctuation(element)
                    if punc:
                        markup += self._Punctuation(punc)
        markup += self._Timestamp()
        return markup

    def WriteDoc(self, corpus_entry):
        """Generates and writes output text for the glossed version of the Chinese document.

        Args:
          corpus_entry: the corpus entry for the source document.

        Returns:
          The file name that the output text was written to.

        Raises:
          BDictException: If the input file does not exist
        """
        infile = corpus_entry['plain_text']
        period_pos = infile.find('.')
        outfile = DEFAULT_OUTFILE_HTML
        if 'gloss_file' in corpus_entry:
            outfile = corpus_entry['gloss_file']
            if self._CheckGlossDirectory():
                gloss_directory = self._CheckGlossDirectory()
                outfile = '%s/%s' % (gloss_directory, outfile)
        else:
            # Give information about possible problem in corpus entry
            print('gloss_file is not in corpus_entry')
            print('infile: %s' % infile)
            if 'source_name' in corpus_entry:
              print('source_name: %s' % corpus_entry['source_name'])
            else:
              print('source_name: none')
            if 'reference' in corpus_entry:
              print('reference: %s' % corpus_entry['reference'])
            else:
              print('reference: none')
        markup = self.GenerateDoc(corpus_entry)
        with codecs.open(outfile, 'w', "utf-8") as outf:
            outf.write(markup)
            outf.close()
        return outfile

    def _CheckGlossDirectory(self):
        """If the directory does not already exist it will be created.
        """
        dirname = self.config['gloss_directory']
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return dirname

    def _extractPunc(self, element):
        """Extract punctuation from the element, returning the pair
        """
        i = element.find('|')
        return (element[i:], element[:i])

    def _Paragraph(self, text):
        """Generates output text formatted for a paragraph.
        """
        return '<p>%s</p>\n' % text

    def _Phrase(self, element_text, phrase_entry):
        """Generates output text formatted for a phrase.
        """
        gloss = phrase_entry['english']
        # print('Output for phrase "%s"' % gloss)
        entry_id = phrase_entry['id']
        url = '/buddhistdict/phrase_detail.php?id=%s' % entry_id
        return '<a href="%s" \n title="%s">%s</a> ' % (url, gloss, element_text)

    def _Punctuation(self, element_text):
        """Generates output text formatted for a punctuation element.
        """
        if element_text == '\n':
            return '<br/>\n'
        match = re.search('\|\|\d\|\|', element_text)
        if match:
            return '%s<br/><br/>\n' % element_text
        match = re.search('\|\|', element_text)
        if match:
            return '%s<br/><br/>\n' % element_text
        return '%s ' % element_text

    def _Title2(self, text):
        """Generates output text formatted for a level 2 header.
        """
        return '<h2>%s</h2>\n' % text

    def _Timestamp(self):
        """Creates a timestamp if the docs is HTML
        """
        return '<br/><p>Page last updated on %s.</p>\n' % date.isoformat(date.today())

    def _Word(self, element_text, entry):
        """Generates output text formatted for a word.
        """
        # print('_Word element_text = %s' % element_text)
        gloss = entry['english']
        entry_id = entry['id']
        # print('_Word entry_id = %s' % entry_id)
        url = '/buddhistdict/sanskrit_query.php?word=%s' % element_text
        return '<a href="%s" title="%s">%s</a> ' % (url, gloss, element_text)
