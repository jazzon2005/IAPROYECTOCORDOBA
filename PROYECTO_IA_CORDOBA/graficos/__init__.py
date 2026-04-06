#No los vaya a borrar, son archivos que incluso vacios, le dicen al programa: "Oye, esta carpeta 
#no es solo una carpeta normal de tu computadora, es un paquete (módulo) de código". Si no existieran,
#se tendrían que hacer una importación del tipo /modelo/celda.py que es propenso a errores, teniendo el 
#__init__.py en las carpetas, python entiende estas como un modulo y permite importar los scripts como:
#from ia.nodo import Nodo