# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import datetime, timedelta
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
import os
import base64
from odoo import modules
from zipfile import ZipFile
import ntpath
import glob

from odoo.tools import config

class DiPdfFileWriter(PdfFileWriter):

    def updateCheckboxValues(self, page, fields):

        for j in range(0, len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()
            for field in fields:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/V"): NameObject(fields[field]),
                        NameObject("/AS"): NameObject(fields[field])
                    })


class DiCerfaWiz(models.TransientModel):
    _name = "di.cerfa.wiz"
    _description = "Wizard de génération de cerfa"

    zipdatas = fields.Binary('Datas', readonly=True, attachment=True)
    zipname = fields.Char(string='Filename', size=256, readonly=True)

    def di_generer_cerfa(self):
        saleorderlines = self.env['sale.order'].browse(
            self.env.context['active_ids']).mapped("order_line")
# .filtered(lambda sol: sol.qty_delivered > 0)
        # ospath = os.getcwd()
        
        """               
        _pdf ='/static/description/cerfa_15063-03.pdf'
        pdf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), _pdf)
        #pdf_client = Client('file:///%s' % pdf_path.lstrip('/'))
        
        _zip ='/temp/' + self.zipname
        zip_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), _zip)
        #zip_client = Client('file:///%s' % zip_path.lstrip('/'))
        """
        
        path = modules.get_module_path('marinove_dev')
        #path_to_data_directory = os.path.join(config['data_dir'], "filestore", self.env.cr.dbname)
        _filestore = tools.config.filestore(self._cr.dbname)
        
        self.zipname = 'cerfas_' + datetime.now().strftime("%d%m%Y%H%M%S%f")\
                       + '.zip'

        #zipfic = path+'/temp/' + self.zipname
        zipfic = os.path.join(_filestore, self.zipname)
        
        lstfiles = []
        for sol in saleorderlines:
            if sol.product_id.di_cerfa:
                with open(path+'/static/description/cerfa_15063-03.pdf',
                      'rb') as fic:
                    pdforig = PdfFileReader(fic)
                    if "/AcroForm" in pdforig.trailer["/Root"]:
                        pdforig.trailer["/Root"]["/AcroForm"].update(
                            {NameObject("/NeedAppearances"): BooleanObject(True)}
                            )
                    pdfdest = DiPdfFileWriter()
                    try:
                        # get the AcroForm tree
                        if "/AcroForm" not in pdfdest._root_object:
                            pdfdest._root_object.update({
                                NameObject("/AcroForm"):
                                IndirectObject(len(pdfdest._objects), 0, pdfdest)
                            })

                        need_appearances = NameObject("/NeedAppearances")
                        pdfdest._root_object["/AcroForm"][need_appearances] \
                            = BooleanObject(True)

                    except Exception as e:
                        print('set_need_appearances_writer() catch : ', repr(e))

                    if "/AcroForm" in pdfdest._root_object:
                        pdfdest._root_object["/AcroForm"].update(
                            {NameObject("/NeedAppearances"): BooleanObject(True)}
                        )

                    page = pdforig.getPage(0)

                    fields_raw = pdforig.getFields()
                    fields = sorted(
                        list(fields_raw.keys()), key=lambda x: x)

                    pdfdest.addPage(page)

                    pdfdest.updatePageFormFieldValues(pdfdest.getPage(0),
                        {
                        # 'Adresse', # Adresse
                        fields[1]: sol.company_id.street \
                        and sol.company_id.street or ' ',
                        # fields[2]: 'Adresse CP', # Adresse CP
                        # 'Adresse dest', # Adresse dest
                        fields[3]: sol.order_id.partner_shipping_id.street \
                        and sol.order_id.partner_shipping_id.street or ' ',
                        # fields[4]: 'Adresse reparcage', # Adresse reparcage
                        # fields[5]: 'Adresse reparcage 2', # Adresse reparcage 2
                        # 'Agrement dest', # Agrement dest
                        # fields[6]: sol.order_id.partner_id.di_agrement,
                        # fields[7]: 'Agrement destinataire', # Agrement dest
                        # 'Bateau', # Bateau
                        fields[9]: sol.company_id.siret \
                        and sol.company_id.siret or ' ',
                        # fields[11]: 'Code 1', # Code 1
                        # fields[12]: 'Code 2', # Code 2
                        # 'Commune dest', # Commune dest
                        fields[13]: (sol.order_id.partner_shipping_id.zip
                                 and sol.order_id.partner_shipping_id.zip
                                 or ' ') + ' ' \
                        + (sol.order_id.partner_shipping_id.city
                           and sol.order_id.partner_shipping_id.city or ' '),
                        # 'Commune 1', # Commune 1
                        fields[14]: (sol.company_id.zip
                                 and sol.company_id.zip or ' ') + ' ' \
                        + (sol.company_id.city and sol.company_id.city
                           or ' '),
                        # fields[15]: 'Commune 2', # Commune 2
                        # fields[16]: 'Date purif', # Date purif
                        # 'Date 1', # Date 1
                        fields[17]: sol.order_id.date_order \
                        and sol.order_id.date_order.strftime('%d/%m/%Y') or ' ',
                        # fields[18]: 'Date 2', # Date 2
                        # fields[19]: 'Date 3', # Date 3
                        # fields[20]: 'Duree purif', # Duree purif
                        # fields[21]: 'Duree reparcage', # Duree reparcage
                        # 'Espece 1', # Espece 1
                        fields[23]: (sol.product_id.name
                                 and sol.product_id.name or ' '),  # \
                        # + (sol.di_nom_sci and sol.di_nom_sci or ' '),
                        # fields[24]: 'Espece 2', # Espece 2
                        # fields[25]: 'Espece 3', # Espece 3
                        # 'Nom', # Nom
                        fields[30]: sol.company_id.name \
                        and sol.company_id.name or ' ',
                        # 'Nom dest', # Nom dest
                        fields[31]: sol.order_id.partner_shipping_id.name \
                        and sol.order_id.partner_shipping_id.name or ' ',
                        # 'Numero DE', # Numero DE
                        fields[32]: sol.order_id.warehouse_id.di_sanit
                        and sol.order_id.warehouse_id.di_sanit or ' ',
                        # 'Quantite 1', # Quantite 1
                        # fields[35]: (sol.qty_delivered
                        #              and sol.qty_delivered or ' '),
                        fields[35]: (sol.product_uom_qty \
                                 and sol.product_uom_qty or ' '),
                        # fields[36]: 'Quantite 2', # Quantite 2
                        # fields[37]: 'Quantite 3', # Quantite 3
                        # fields[39]: sol.di_zonep_id.name,  # 'Zone', # Zone
                    })

                    pdfdest.updateCheckboxValues(page, {
                         fields[22]: '/Yes', # Eleveur
                        # fields[33]: '/Yes', # Pecheur
                        # fields[34]: '/Yes', # Purificateur
                        #fields[29]: '/Yes',  # Negociant
                        # fields[26]: '/Yes', # HAM halle a marée
                        # fields[0]: '/Yes', # Coche A
                        #fields[8]: '/Yes',  # Coche B
                        # fields[10]: '/Yes', # Coche C
                        # fields[28]: '/Yes', # Non classé
                        # fields[40]: '/Yes', # Eleveur 2
                        fields[41]: '/Yes',  # Expediteur
                        # fields[43]: '/Yes', # purificateur 2
                        fields[42]: '/Yes',  # Negociant2
                        # fields[27]: '/Yes', # HAM2
                        # fields[38]: '/Yes', # Transfo

                    })
                    # FIELDS_RAW2 = PDFORIG.GETfIELDS()
                    # IF NOT OS.PATH.EXISTS(OSPATH+"/CERFA"):
                    #     OS.MKDIR(OSPATH+"/CERFA")

                    code_prod = sol.product_id.default_code or "_"
                    #filename = path+'/temp/cerfa_15063-03_' + \
                    #    sol.order_id.name+'_'+sol.product_id.default_code+'_'\
                    #    + datetime.now().strftime("%d%m%Y%H%M%S%f")+'.pdf'
                    
                    """
                    _pdf ='/temp/cerfa_15063-03_' + \
                        sol.order_id.name+'_'+code_prod+'_'\
                        + datetime.now().strftime("%d%m%Y%H%M%S%f")+'.pdf'
                    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), _pdf)
                    """
                    
                    
                    filename = path+'/temp/cerfa_15063-03_' + \
                        sol.order_id.name+'_'+code_prod+'_'\
                        + datetime.now().strftime("%d%m%Y%H%M%S%f")+'.pdf'    
                        
                    _filename = 'cerfa_15063-03_' + \
                        sol.order_id.name+'_'+code_prod+'_'\
                        + datetime.now().strftime("%d%m%Y%H%M%S%f")+'.pdf'     
                    #filename = os.path.join(config['data_dir'], "filestore", self.env.cr.dbname, _filename)   
                    filename = os.path.join(_filestore, _filename)
                    lstfiles.append(filename)

                    output = open(filename, 'xb')
                    pdfdest.write(output)
                    output.close()
                
                
        if lstfiles:
            with ZipFile(zipfic, 'w') as zip:
                for filetozip in lstfiles:
                    zip.write(filetozip, ntpath.basename(filetozip))
                    os.remove(filetozip)
            zip.close()
            with open(zipfic, "rb") as f:
                bytes = f.read()
                zipvalue = base64.b64encode(bytes)
            self.write({
                'zipdatas': zipvalue,
                'zipname': self.zipname,
            })
        os.remove(zipfic)
        return {
            'type': 'ir.actions.act_url',
                    'url': "web/content/?model=di.cerfa.wiz&id="
                           + str(self.id)
                           + "&filename_field=zipname&field=zipdatas"
                           + "&download=true&filename=" + self.zipname,
                    'target': 'self',
        }

    @api.model
    def default_get(self, fields):
        res = super(DiCerfaWiz, self).default_get(fields)
        return res

    # Call by cron
    # @api.model
    # def autovacuum_temp_files(self):
    #     path = modules.get_module_path('marinove_dev') + '/temp/'
    #     files = glob.glob(path + '*.zip')
    #     for f in files:
    #         if datetime.fromtimestamp(os.path.getmtime(f)) \
    #            < (datetime.now() - timedelta(days=7)):
    #             os.remove(f)
