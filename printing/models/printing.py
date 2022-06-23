# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import os, sys
import logging

_logger = logging.getLogger(__name__)

class MIADI_EtiquetteImpression(models.Model):
    _name = "di.printing.printing"
    _description = "Printing"
    #_order = "name"
    
    printer_name = fields.Char(string="Printer name", required=True)
    etiquette_text = fields.Text(string="Text of label to print", required=True)
    count = fields.Integer(string="Number of etiquettes to print", required=True,default=1)
    printed = fields.Boolean(string="Is printed ?",default=False)
    printing_date = fields.Datetime(string="Printing date", required=False)
    order_line = fields.Many2one('sale.order.line', string="Linked order line", help="Linked to an order line", required=False)
    order_name = fields.Char(string="Linked order", required=False)
    real_number_etiq = fields.Integer(string="Real number of etiquettes to print", required=False,default=0)
    
    def replace_accent_zpl(self,s):
        # êèéàâáôöîÉÈÊÀÂÁÔÖÎ
        if s:
            s = s.replace('ê', '\\88') \
                 .replace('è', '\\8a') \
                 .replace('é', '\\82') \
                 .replace('à', '\\85') \
                 .replace('â', '\\83') \
                 .replace('á', '\\a0') \
                 .replace('ô', '\\93') \
                 .replace('ö', '\\94') \
                 .replace('î', '\\8c') \
                 .replace('É', '\\90') \
                 .replace('È', '\\d4') \
                 .replace('Ê', '\\d2') \
                 .replace('À', '\\b7') \
                 .replace('Â', '\\b6') \
                 .replace('Á', '\\b5') \
                 .replace('Ô', '\\e2') \
                 .replace('Ö', '\\94') \
                 .replace('Î', '\\d7') \
                 .replace('°', '\\f8')
        return s

    def replace_accent_epl(self,s):
        # êèéàâáôöîÉÈÊÀÂÁÔÖÎ = êèéàâáôöîÉÈÊÀÂÁÔÖÎ
        return s

    def replace_accent_toshiba(self,s):
        # êèéàâáôöîÉÈÊÀÂÁÔÖÎ = ˆŠ‚…ƒ “”ŒÔÒ·¶µâ™×
        if s:
            s = s.replace('ê', 'ˆ') \
                 .replace('è', 'Š') \
                 .replace('é', '‚') \
                 .replace('à', '…') \
                 .replace('â', 'ƒ') \
                 .replace('á', ' ') \
                 .replace('ô', '“') \
                 .replace('ö', '”') \
                 .replace('î', 'Œ') \
                 .replace('É', '') \
                 .replace('È', 'Ô') \
                 .replace('Ê', 'Ò') \
                 .replace('À', '·') \
                 .replace('Â', '¶') \
                 .replace('Á', 'µ') \
                 .replace('Ô', 'â') \
                 .replace('Ö', '™') \
                 .replace('Î', '×')
        return s

    def printetiquetteonwindows(self, printername, etiqname, charSepBegin, charSepEnd, parameters, number_etiquette = 0):
        _logger.warning(printername + '_' + etiqname + charSepBegin + charSepEnd)
        charDelimitor = "§"
        printer = self.env['di.printing.printer'].search([('name', '=', printername), ]) 
        langage_print = printer.langage_print
        etiq = self.env['di.printing.etiqmodel'].search([('name', '=', etiqname), ])
        etiqtext = ""
        if langage_print == "ZPL":
            etiqtext = etiq.text_etiq_zpl        
        if langage_print == "EPL":
            etiqtext = etiq.text_etiq_epl        
        if langage_print == "Toshiba":
            etiqtext = etiq.text_etiq_toshiba        
        contenu = etiqtext 
        
        sale_ordername = ''
        saleline_id = 0
    
        for paramName, value in parameters:
            if paramName == 'sale_ordername':
                sale_ordername = value
            if paramName == "saleline_id":
                saleline_id = value
            if paramName == "saleline_qty":
                number_etiquette = value            
            if contenu.find(charSepBegin + paramName.lower() + charSepEnd) != -1:
                if (value is not None):
                    contenu = contenu.replace(charSepBegin + paramName.lower() + charSepEnd, str(value))
                else:
                    contenu = contenu.replace(charSepBegin + paramName.lower() + charSepEnd, "")
        
        #_logger.debug('A DEBUG message') 
        #_logger.info('An INFO message') 
        #_logger.warning('A WARNING message') 
        #_logger.error('An ERROR message') 
        
        while contenu.find(charSepBegin + "IF" + charDelimitor) != -1:
            #[IF;V1;V2;RY;RN] IF V1==V2 THEN RY ELSE RN
            #contenu = contenu + "if trouvé"
            start_if = contenu.find(charSepBegin + "IF" + charDelimitor)
            end_if = contenu.find(charSepEnd, start_if) +1
            entire_if = contenu[start_if:end_if]
            part_if = entire_if[1:-1].split(charDelimitor)
            V1 = part_if[1].strip()
            if V1 == "false":
                V1 = ""
            V2 = part_if[2].strip()
            if V2 == "false":
                V2 = ""
            #_logger.info(entire_if[1:-1])
            if V1 == V2:
                contenu = contenu.replace(entire_if, part_if[3])
            else:
                contenu = contenu.replace(entire_if, part_if[4])
        while contenu.find(charSepBegin + "LPART" + charDelimitor) != -1:
            #contenu = contenu + "rpart trouvé"
            #[LPART;V;NB] LEFT SUBSTRING FROM V LIMITED TO NB CAR WITH SEARCH PREVIOUS SPACE
            start_part = contenu.find(charSepBegin + "LPART" + charDelimitor)
            end_part = contenu.find(charSepEnd, start_part) +1
            entire_part = contenu[start_part:end_part]
            part_part = entire_part[1:-1].split(charDelimitor)
            #_logger.info(entire_part[1:-1])
            txt = part_part[1].strip()
            maxlen = int(part_part[2])
            if len(txt) <= maxlen:
                contenu = contenu.replace(entire_part, txt)
            else:
                txt = txt[:maxlen]
                i = txt.rfind(" ")
                if i == -1:
                    #previous space not found
                    contenu = contenu.replace(entire_part, part_part[1])
                else :
                    txt = txt[:i]
                    contenu = contenu.replace(entire_part, txt)
        while contenu.find(charSepBegin + "RPART" + charDelimitor) != -1:
            #[RPART;V;NB] RIGHT SUBSTRING FROM V UPPER THAN NB CAR WITH SEARCH PREVIOUS SPACE
            start_part = contenu.find(charSepBegin + "RPART" + charDelimitor)
            end_part = contenu.find(charSepEnd, start_part) +1
            entire_part = contenu[start_part:end_part]
            rpart_part = entire_part[1:-1].split(charDelimitor)
            #_logger.info("ZZZ " + entire_part[1:-1])
            txt = rpart_part[1].strip()
            maxlen = int(rpart_part[2])
            if len(txt) <= maxlen:
                contenu = contenu.replace(entire_part, "")
            else:
                txt = txt[:maxlen]
                i = txt.rfind(" ")
                if i == -1:
                    #previous space not found
                    contenu = contenu.replace(entire_part, rpart_part[1])
                else :
                    txt = txt[:i+1]
                    rtxt = rpart_part[1].strip()
                    rtxt = rtxt.replace(txt, "", 1)
                    contenu = contenu.replace(entire_part, rtxt)
        while contenu.find(charSepBegin + "EVAL" + charDelimitor) != -1:
            #[EVAL;EXPR] EVALUATE EXPRESSION AND PASTE RESULT
            #ie [EVAL;'{:0>4}'.format('[qte]')] if qte = 1 return '0001'
            start_part = contenu.find(charSepBegin + "EVAL" + charDelimitor)
            end_part = contenu.find(charSepEnd, start_part) +1
            entire_part = contenu[start_part:end_part]
            part_eval = entire_part[1:-1].split(charDelimitor)
            txt = part_eval[1].strip()
            txt = eval(txt)
            contenu = contenu.replace(entire_part, txt)
        while contenu.find(charSepBegin + "LINE" + charDelimitor) != -1:
            #[LINE;V;NUMLIG] ONE LINE IN V SEPARATE BY \n (NUMLIG FROM 1 TO xxx)
            start_part = contenu.find(charSepBegin + "LINE" + charDelimitor)
            end_part = contenu.find(charSepEnd, start_part) +1
            entire_part = contenu[start_part:end_part]
            rpart_part = entire_part[1:-1].split(charDelimitor)
            #_logger.info("ZZZ " + entire_part[1:-1])
            txt = rpart_part[1].strip()
            txtpart = txt.split("\n")
            numLine = int(rpart_part[2].strip()) - 1
            _logger.info("NumLine " + str(numLine))
            _logger.info(" in " + txt)
            _logger.info(" txt_nb_part " + str(len(txtpart)))
            if txtpart[numLine]:
                contenu = contenu.replace(entire_part, txtpart[numLine])
            else:
                contenu = contenu.replace(entire_part, "")
             
        if langage_print == "ZPL":
            contenu = self.replace_accent_zpl(contenu)
        if langage_print == "EPL":
            contenu = self.replace_accent_epl(contenu)
        if langage_print == "Toshiba":
            contenu = self.replace_accent_toshiba(contenu)
        
        if sys.version_info >= (3,):
            raw_data = bytes(contenu, "utf-8")
        else:
            raw_data = contenu

        printing_vals = {
        'printer_name': printer.name,
        'etiquette_text': contenu,
        'count': 1,
        'printed': False,
        'order_line': saleline_id,
        'order_name': sale_ordername,
        'real_number_etiq': number_etiquette,
        }
        self.env['di.printing.printing'].create(printing_vals)
    