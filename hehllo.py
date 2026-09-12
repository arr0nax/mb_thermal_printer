from escpos.printer import Serial
""" 9600 Baud, 8N1, Flow Control Enabled """
p = Serial(devfile='/dev/serial0',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)
p.text("Hello World\n")
p.image("card.png")
p.barcode('4006381333931', 'EAN13', 64, 2, '', '')
p.cut()
