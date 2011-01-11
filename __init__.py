#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, codecs, mimetypes, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

from plasTeX.Config import config
from plasTeX.ConfigManager import *

# Basicamente copiado do renderizador XHTML 
class WGHTML(_Renderer):
    """ Renderer for XHTML documents """

    # Ajusta os parametros de configuração para que os arquivos sejam gerados em OEBPS/
    config['images']['filenames'] = 'OEBPS/' + config['images']['filenames']
    # Consertar as URLs OEBPS/images/img-????.png...
    config['images']['base-url'] = '..'

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        # Chamadas para geracao dos arquivos opf e ncx
        self.doOPFFiles(document)
        self.doNCXFiles(document)
        return res

    def processFileContent(self, document, s):
        config['files']['directory'] += 'OEBPS/'
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
            # Ajuste das tags solitarias: <tag /> (copiado da funcao anterior)
            toc = re.compile(r'(<(?:hr|br|img|link|meta)\b.*?)\s*/?\s*(>)', 
                             re.I|re.S).sub(r'\1 /\2', toc)
 

            # O arquivo content.opf sera gerado no diretorio OEBPS/
            f = codecs.open('OEBPS/content.opf', 'w', encoding, errors='xmlcharrefreplace')
            # Insere o cabecalho xml que nao e colocado corretamente via template
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')


            # Move o arquivo index.html para o diretorio OEBPS/
#            os.rename('index.html', 'OEBPS/index.html')

            # Move os arquivos das seções
            spineopf = '<itemref idref="index" />\n' # index.html
            for arq in os.listdir('.'):
                if re.match('.*\.html', arq): # Nao funciona para um diretorio .html
                    os.rename(arq, 'OEBPS/' + arq)
                    spineopf += '<itemref idref="%s" />\n' % (re.sub('\..*$', '', arq))

            toc = re.sub('</spine>', spineopf + "</spine>", toc)
                        

            # Adiciona o mimetype do arquivo ncx
            mimetypes.add_type('application/x-dtbncx+xml', '.ncx')
            
            # Muda para XHTML
            mimetypes.add_type('application/xhtml+xml', '.html')

            itemopf = ''
            for root, dirs, arquivos in os.walk('OEBPS/'):
                for nomeArquivo in arquivos:
                    if (nomeArquivo == 'content.opf'):
                        continue

                    href = os.path.join(re.sub('OEBPS/?', '', root), nomeArquivo)
                    # As / são substituídas por - no id
                    itemid = re.sub('\..*$', '', re.sub('/', '-', href))
                    mediaType = mimetypes.guess_type(nomeArquivo)[0]

                    itemopf += '<item id="%s" href="%s" media-type="%s"></item>\n' % (itemid, href, mediaType)
    
            toc = re.sub('</manifest>', itemopf + "</manifest>", toc)
            f.write(toc)
            f.close()

    def doNCXFiles(self, document, encoding='UTF-8'):
        """ Gerador do arquivo content.opf """
        latexdoc = document.getElementsByTagName('document')[0]

        if 'toc-ncx' in self:
            toc = self['toc-ncx'](latexdoc)
#            toc = re.sub(r'\s*/\s*>', r'>', toc)
#            toc = re.sub(r'(<param)(\s+[^>]*)(\s+name="[^"]*")(\s*>)', r'\1\3\2$
            toc = re.compile(r'(<(?:item|br|img|link|meta)\b.*?)\s*/?\s*(>)', 
                             re.I|re.S).sub(r'\1 /\2', toc)

            # Force XHTML syntax on empty tags
            f = codecs.open('OEBPS/toc.ncx', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
            f.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n\t"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n')
    
            f.write(toc)
            f.close()

Renderer = WGHTML
