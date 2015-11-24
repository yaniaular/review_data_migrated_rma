#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import oerplib

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user", help="Admin odoo user",
                    default="admin")
parser.add_argument("-p", "--passwd", help="Admin odoo password",
                    default="admin")
parser.add_argument("-d", "--db", help="database name",
                    default="yoy")
args = parser.parse_args()

DB = args.db
oerp = oerplib.OERP()
oerp.config['timeout'] = 4000
oerp.login(user=args.user, passwd=args.passwd, database=DB)

cl_obj = oerp.get('claim.line')
repair_obj = oerp.get('mrp.repair')

ir_model_data_obj = oerp.get('ir.model.data')

repairs = repair_obj.search([('state', '=', 'draft')])
for rep in repairs:
    try:
        oerp.exec_workflow('mrp.repair','repair_confirm', rep)
    except:
        rep_brw = repair_obj.browse(rep)
        line_id = rep_brw.claim_line_id.id
        xml_id = ir_model_data_obj.search(
            [('res_id', '=', line_id), ('model', '=', 'claim.line')])
        xml_id = ir_model_data_obj.read(xml_id, ['name'])[0]
        name = xml_id.get('name')
        print "Repair of claim_line %s is not diagnosed " % name


claim_lines = cl_obj.search([('state', '=', 'diagnosed'), ])
                             # ('claim_type', '=', 1)])
different = 0
all_false = 0
do_not_know = 0
for line in claim_lines:
    line_brw = cl_obj.browse(line)

    quant_id = [q for q in line_brw.move_in_id.quant_ids]
    quant_id = quant_id[0]
    lot = quant_id.lot_id

    xml_id = ir_model_data_obj.search(
        [('res_id', '=', line), ('model', '=', 'claim.line')])
    xml_id = ir_model_data_obj.read(xml_id, ['name'])[0]
    name = xml_id.get('name')

    if line_brw.prodlot_id != lot:
        print "Case#1 claim_line %s has prodlot different to the lot of move " % name
        print line_brw.prodlot_id, lot
        print "\n"
        different += 1
    elif line_brw.prodlot_id is False and lot is False:
        try:
            oerp.execute('claim.line',
                        'end_repair', [line])
            oerp.execute('claim.line',
                        'product_delivered', [line])
            oerp.execute('claim.line',
                        'receive_from_workshop', [line])
        except:
            print "Case#2 claim_line %s has prodlot and the lot of move is False" % name
            print line_brw.prodlot_id, lot
            print "\n"
            all_false += 1
    else:
        try:
            oerp.execute('claim.line',
                        'end_repair', [line])
            oerp.execute('claim.line',
                        'product_delivered', [line])
            oerp.execute('claim.line',
                        'receive_from_workshop', [line])
            print "Good \n"
        except:
            print "Case#3 claim_line %s I don't know" % name
            print line_brw.prodlot_id, lot
            print "\n"
            do_not_know += 1


print "Case#1 %s cases of claim_line has prodlot different to the lot of move" % str(different)
print "Case#2 %s claim_line has prodlot and the lot of move is False" % str(all_false)
print "Case#3 %s claim_line I don't know" % str(do_not_know)
print "%s Total" % str(len(claim_lines))
