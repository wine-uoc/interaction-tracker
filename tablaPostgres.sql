
CREATE TABLE rssiphonedata (
  id BIGINT PRIMARY KEY,
  srcdevice VARCHAR(32),  --el que esta haciendo el advertising
  dstdevice VARCHAR(128), --el que escanea y envia esta tupla a la DB 
  rssi VARCHAR(4),
  ustime VARCHAR(16)
);








--no la uso de momento
CREATE TABLE rssianchordata (
  id BIGINT PRIMARY KEY,
  launchpadId VARCHAR(32),
  devName VARCHAR(128) NOT NULL,
  rssi VARCHAR(4),
  ustime VARCHAR(16)
);

--No usadas de momento
CREATE TABLE acceldata (
  id SERIAL PRIMARY KEY,
  devName VARCHAR(128) NOT NULL,
  x_acc VARCHAR(16),
  y_acc VARCHAR(16),
  z_acc VARCHAR(16)
);

CREATE TABLE orientationdata (
  id SERIAL PRIMARY KEY,
  devName VARCHAR(128) NOT NULL,
  x_ori VARCHAR(16),
  y_ori VARCHAR(16),
  z_ori VARCHAR(16)
);
