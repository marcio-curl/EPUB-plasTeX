#!/usr/bin/env python

import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

from plasTeX.Config import config
from plasTeX.ConfigManager import *


class WGHTML(_Renderer):
    """ Renderer for XHTML documents """

    # Coloca os arquivos gerados em OEBPS/
    config['files']['filename'] = 'OEBPS/' + config['files']['filename']

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        self.doOPFFiles(document)
        self.doNCXFiles(document)
        return res

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Force XHTML syntax on empty tags
        s = re.compile(r'(<(?:hr|br|img|link|meta)\b.*?)\s*/?\s*(>)', 
                       re.I|re.S).sub(r'\1 /\2', s)

        # Remove empty paragraphs
        s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Add a non-breaking space to empty table cells
        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)
        
        return s
    
    def doOPFFiles(self, document, encoding='UTF-8'):
        """ Gerador do arquivo content.opf """
        latexdoc = document.getElementsByTagName('document')[0]

        if 'content-opf' in self:
            toc = self['content-opf'](latexdoc)
#            toc = re.sub(r'\s*/\s*>', r'>', toc)
#            toc = re.sub(r'(<param)(\s+[^>]*)(\s+name="[^"]*")(\s*>)', r'\1\3\2$

            # Force XHTML syntax on empty tags
            f = codecs.open('OEBPS/content.opf', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
            f.write(toc)
            f.close()

    def doNCXFiles(self, document, encoding='UTF-8'):
        """ Gerador do arquivo content.opf """
        latexdoc = document.getElementsByTagName('document')[0]

        if 'toc-ncx' in self:
            toc = self['toc-ncx'](latexdoc)
#            toc = re.sub(r'\s*/\s*>', r'>', toc)
#            toc = re.sub(r'(<param)(\s+[^>]*)(\s+name="[^"]*")(\s*>)', r'\1\3\2$

            # Force XHTML syntax on empty tags
            f = codecs.open('OEBPS/toc.ncx', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
            f.write(toc)
            f.close()

Renderer = WGHTML 
