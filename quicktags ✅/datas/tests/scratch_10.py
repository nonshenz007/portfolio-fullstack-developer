# convert_font_to_bytes.py
font_path = 'arialbd.ttf'
output_file = 'EmbeddedFont.py'

with open(font_path, 'rb') as f:
    font_bytes = f.read()

with open(output_file, 'w') as f:
    f.write('FONT_BYTES = ')
    f.write(repr(font_bytes))