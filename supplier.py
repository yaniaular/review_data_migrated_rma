import oerplib
import argparse

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
stock_quant_obj = oerp.get('stock.quant')

################################################################
print "\n************sent_supplier\n"
claim_lines = cl_obj.search([('state', 'in', ['sent_supplier'])])
for line in claim_lines:

    xml_id = ir_model_data_obj.search(
        [('res_id', '=', line), ('model', '=', 'claim.line')])
    xml_id = ir_model_data_obj.read(xml_id, ['name'])[0]
    name = xml_id.get('name')
    line_brw = cl_obj.browse(line)

    # to verify empty fields
    if line_brw.workshop_in_move_id is not False:
        print "error: %s tiene workshop_in_move_id" % name
    if line_brw.replace_move_id is not False:
        print "error: %s tiene replace_in_move_id" % name
    if line_brw.receipt_claim_move_id is not False:
        print "error: %s tiene receipt_in_move_id" % name
    if line_brw.refurbish_move_id is not False:
        print "error: %s tiene refurbish_in_move_id" % name
    if line_brw.stock_move_id is not False:
        print "error: %s tiene stock_move_id" % name

    # to verify field move_in_id
    if not line_brw.move_in_id:
        print "error: %s Debe tener move_in_id %s" % name
    else:
        if line_brw.move_in_id.state != 'draft':
            print "error: %s Debe tener move_in_id en draft" % name

        if line_brw.prodlot_id:
            quant_reserved = stock_quant_obj.search([("lot_id",
                                                    "=",
                                                    line_brw.prodlot_id.id)])

            if len(quant_reserved) > 1:
                print "error: %s hay demasiados quants para el lote" % line_brw.prodlot_id.id
            if len(quant_reserved) == 0:
                print "error: %s no hay quant para el lote" % line_brw.prodlot_id.id
            if len(quant_reserved) == 1:
                quant_reserved = stock_quant_obj.browse(quant_reserved[0])
                if quant_reserved and \
                        quant_reserved.reservation_id is not True:
                    print "error: %s El move_in_id no tiene quant reservado" % name


    # to verify field move_out_id
    if not line_brw.move_out_id:
        print "error: %s Debe tener move_out_id" % name
    else:
        if line_brw.move_out_id.state != 'done':
            print "error: %s Debe tener move_out_id en done" % name
        if len(line_brw.move_out_id.quant_ids) > 1:
            print "error: %s en move_out_id tiene mas de 1 quant" % name
        if len(line_brw.move_out_id.quant_ids) == 0:
            print "error: %s en move_out_id no tiene quant" % name
        if len(line_brw.move_out_id.quant_ids) == 1:
            quant_id = [q for q in line_brw.move_out_id.quant_ids]
            quant_id = quant_id[0]
            if quant_id.lot_id != line_brw.prodlot_id:
                print "error: %s en move_out_id los lotes no coinciden (%s,%s)" % \
                (name, quant_id.lot_id, line_brw.prodlot_id)
            if quant_id.product_id != line_brw.product_id:
                print "error: %s en move_out_id los "
                "productos no coinciden" % name
        if line_brw.move_in_id:
            if quant_id.reservation_id != line_brw.move_in_id:
                print "error: %s El move_in_id no tiene quant reservado" % name

###########################################################
print "\n************collected\n"
claim_lines = cl_obj.search([('state', 'in', ['collected'])])
for line in claim_lines:

    xml_id = ir_model_data_obj.search(
        [('res_id', '=', line), ('model', '=', 'claim.line')])
    xml_id = ir_model_data_obj.read(xml_id, ['name'])[0]
    name = xml_id.get('name')
    line_brw = cl_obj.browse(line)

    # to verify empty fields
    if line_brw.workshop_in_move_id is not False:
        print "error: %s tiene workshop_in_move_id" % name
    if line_brw.replace_move_id is not False:
        print "error: %s tiene replace_in_move_id" % name
    if line_brw.receipt_claim_move_id is not False:
        print "error: %s tiene receipt_in_move_id" % name
    if line_brw.refurbish_move_id is not False:
        print "error: %s tiene refurbish_in_move_id" % name
    if line_brw.stock_move_id is not False:
        print "error: %s tiene stock_move_id" % name

    # to verify field move_in_id
    if not line_brw.move_in_id:
        print "error: %s Debe tener move_in_id %s" % name
    else:
        if line_brw.move_in_id.state != 'done':
            print "error: %s Debe tener move_in_id en done" % name

        quant_id = False
        if len(line_brw.move_in_id.quant_ids) > 1:
            print "error: %s hay demasiados quants para el lote" % line_brw.prodlot_id.id
        if len(line_brw.move_in_id.quant_ids) == 0:
            print "error: %s no hay quant para el lote" % line_brw.prodlot_id.id
        if len(line_brw.move_in_id.quant_ids) == 1:
            quant_id = [q for q in line_brw.move_in_id.quant_ids]
            quant_id = quant_id[0]
            if quant_id.lot_id != line_brw.prodlot_id:
                print "error: %s en move_in_id los lotes no coinciden (%s,%s)" % \
                    (name, quant_id.lot_id, line_brw.prodlot_id)
            if quant_id.product_id != line_brw.product_id:
                print "error: %s en move_in_id los "
                "productos no coinciden" % name


    # to verify field move_out_id
    if not line_brw.move_out_id:
        print "error: %s Debe tener move_out_id" % name
    else:
        if line_brw.move_out_id.state != 'done':
            print "error: %s Debe tener move_out_id en done" % name
        if len(line_brw.move_out_id.quant_ids) > 1:
            print "error: %s en move_out_id tiene mas de 1 quant" % name
        if len(line_brw.move_out_id.quant_ids) == 0:
            print "error: %s en move_out_id no tiene quant" % name
        if len(line_brw.move_out_id.quant_ids) == 1:
            quant_id_2 = [q for q in line_brw.move_out_id.quant_ids]
            quant_id_2 = quant_id_2[0]
            if quant_id_2.lot_id != line_brw.prodlot_id:
                print "error: %s en move_out_id los lotes no coinciden (%s,%s)" % \
                (name, quant_id_2.lot_id, line_brw.prodlot_id)
            if quant_id_2.product_id != line_brw.product_id:
                print "error: %s en move_out_id los "
                "productos no coinciden" % name
            if quant_id != quant_id_2:
                print "error: %s en move_out_id move_in_id los lotes no coinciden" % \
                    (name, quant_id.lot_id, quant_id_2.lot_id)


###########################################################
print "\n************credit_note\n"
claim_lines = cl_obj.search([('state', '=', 'credit_note'),
                             ('claim_type', '=', 2)])

for line in claim_lines:
    xml_id = ir_model_data_obj.search(
        [('res_id', '=', line), ('model', '=', 'claim.line')])
    xml_id = ir_model_data_obj.read(xml_id, ['name'])[0]
    name = xml_id.get('name')
    line_brw = cl_obj.browse(line)
    if line_brw.workshop_in_move_id is not False:
        print "error: %s tiene workshop_in_move_id" % name
    if line_brw.replace_move_id is not False:
        print "error: %s tiene replace_in_move_id" % name
    if line_brw.receipt_claim_move_id is not False:
        print "error: %s tiene receipt_in_move_id" % name
    if line_brw.refurbish_move_id is not False:
        print "error: %s tiene refurbish_in_move_id" % name
    if line_brw.stock_move_id is not False:
        print "error: %s tiene stock_move_id" % name


    if line_brw.move_in_id is not False:
        print "error: %s tiene move_in_id" % name
    if not line_brw.move_out_id:
        print "error: %s no tiene move_out_id" % name
    else:
        if line_brw.move_out_id.state != 'done':
            print "error: %s Debe tener move_out_id en done" % name
        if len(line_brw.move_out_id.quant_ids) > 1:
            print "error: %s en move_out_id tiene mas de 1 quant" % name
        if len(line_brw.move_out_id.quant_ids) == 0:
            print "error: %s en move_out_id no tiene quant" % name
        if len(line_brw.move_out_id.quant_ids) == 1:
            quant_id = [q for q in line_brw.move_out_id.quant_ids]
            quant_id = quant_id[0]
            if quant_id.lot_id != line_brw.prodlot_id:
                print "error: %s en move_out_id los lotes no coinciden (%s,%s)" % \
                (name, quant_id.lot_id, line_brw.prodlot_id)
            if quant_id.product_id != line_brw.product_id:
                print "error: %s en move_out_id los "
                "productos no coinciden" % name
