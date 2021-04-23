# interaction-tracker

## Versión Borja y Marc

- Tag modo advertise
- Anchor modo scan
 
	
### Anchors
- Ejecutan el proyecto **simple_observer_cc2640r2lp_app_Trabajo_BorjaMarc**

### Tags
- Ejecutan la aplicación **positioningApp**

### Script lectura puertos serie
- Ejecutan script **ReadAnchorData_BorjaMarc.py**
- Va leyendo la información de los puertos serie de los anchors y lo guarda en el fichero *output.json*

## Versión estándard

- Tag modo advertise/scan
- Anchor modo scan

### Anchors
- Ejecutan el proyecto **simple_observer_cc2640r2lp_app_Trabajo**

### Tags
- Ejecutan la aplicación **positioningApp**

### Script lectura puertos serie
- Ejecutan script **ReadAnchorData**
- Va leyendo la información de los puertos serie de los anchors y los envía a Node-RED, donde se guardan en una base de datos en PostgreSQL.
