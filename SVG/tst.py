import xml.etree.ElementTree as ET

tree = ET.parse("Template.svg")
root = tree.getroot()

print("viewBox:", root.attrib.get('viewBox'))
print("width/height raíz:", root.attrib.get('width'), root.attrib.get('height'))

parent_map = {hijo: padre for padre in root.iter() for hijo in padre}
role_elem = root.find('.//*[@id="role"]')
if role_elem is not None:
    padre = parent_map.get(role_elem)
    print("Padre de 'role':", padre.tag, padre.attrib)