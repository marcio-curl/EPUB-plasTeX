#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, codecs, mimetypes, uuid, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

from plasTeX.Config import config
from plasTeX.ConfigManager import *

# Basicamente copiado do renderizador XHTML 
class WGHTML(_Renderer):
    """ Renderizador coxa para ePUB """

    # Ajusta os parametros de configuração para que os arquivos sejam gerados em OEBPS/
    config['images']['filenames'] = 'OEBPS/' + config['images']['filenames'] # Teremos problemas se usarmos multiplos templates.
    # "Conserta" as URLs OEBPS/images/img-????.png
    config['images']['base-url'] = '..'
    
    # Extensões de arquivos utilizadas
    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def cleanup(self, document, files, postProcess=None):        
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)

        # Move os arquivos de conteúdo para OEBPS/
        for arq in files:
            os.rename(arq, 'OEBPS/' + arq)

        latexdoc = document.getElementsByTagName('document')[0]

        # Cria uma entrada para o bookid com um UUID aleatório.
        latexdoc.setUserData('bookid', 'urn:uuid:%s' % uuid.uuid4())

        # Adiciona o mimetype do arquivo ncx
        if not mimetypes.types_map.has_key('.ncx'):
            mimetypes.add_type('application/x-dtbncx+xml', '.ncx')

        # Muda os aquivos .html para XHTML
        mimetypes.add_type('application/xhtml+xml', '.html')

        # Mimetype para fontes OpenType
        if not mimetypes.types_map.has_key('.otf'):
            mimetypes.add_type('application/vnd.ms-opentype', '.otf')

        # Gera o arquivo ncx
        self.doNCXFiles(latexdoc)

        listaArquivos = dict() # Lista dos arquivos no manifest
        spine = [] # Lista de ids no spine (poderiamos trocar por uma função que verifica quais tipos de seção geram arquivos e incluir no userdata deles).
        for root, dirs, arquivos in os.walk('OEBPS/'):
            for nomeArquivo in arquivos:
                if (nomeArquivo == 'content.opf'):
                    continue

                if re.match('.*~$', nomeArquivo):
                    continue

                href = os.path.join(re.sub('OEBPS/?', '', root), nomeArquivo)
                # As / são substituídas por - no id
                itemid = re.sub('\..*$', '', re.sub('/', '-', href))
                mediaType = mimetypes.guess_type(nomeArquivo)[0]

                # Os arquivos html são incluídos no spine
                if re.match('.*\.html', nomeArquivo):
                    spine.append(itemid)

                listaArquivos[itemid] = {'href': href, 'mediaType': mediaType}
            
        latexdoc.setUserData('listaArqs', listaArquivos)
        # A lista de ids será ordenada para a geração do content.opf
        latexdoc.setUserData('spine', sorted(spine))

        # Chamadas para geração do arquivo opf
        self.doOPFFiles(latexdoc)
        return res

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Fecha as tags solitárias como em <br />
        s = re.compile(r'(<(?:hr|br|img|link|meta)\b.*?)\s*/?\s*(>)', 
                       re.I|re.S).sub(r'\1 /\2', s)

        # Remove os parágrafos vazios
        s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Espaço nas células vazias das tabelas
        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)

        # Sem ":" nos ids
#        s = re.compile(r'id="(.*?):(.*?)"', re.I).sub(r'id="\1\2"', s)
        s = re.compile(r'<(\w+) id="(.*?):(.*?)"(.*?)>', re.I | re.U).sub(r'<\1 id="\2\3"\4>', s)

        return s
    
    def doOPFFiles(self, latexdoc, encoding='UTF-8'):
        """ Gerador do arquivo content.opf """

        if 'content-opf' in self:            
            toc = self['content-opf'](latexdoc)

            # Ajuste das tags solitárias
            toc = re.compile(r'></(?:item|itemref)>', re.I|re.S).sub(r' />\n', toc)
 

            # O arquivo content.opf será gerado no diretório OEBPS/
            f = codecs.open('OEBPS/content.opf', 'w', encoding, errors='xmlcharrefreplace')
            # Insere o cabecalho xml que não é colocado corretamente via template
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')

            f.write(toc)
            f.close()


    def doNCXFiles(self, latexdoc, encoding='UTF-8'):
        """ Gerador do arquivo toc.ncx """

        if 'toc-ncx' in self:
            toc = self['toc-ncx'](latexdoc)

            f = codecs.open('OEBPS/toc.ncx', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
            f.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n\t"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n')
    
            f.write(toc)
            f.close()

Renderer = WGHTML
