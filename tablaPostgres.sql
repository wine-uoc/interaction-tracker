CREATE TABLE data (
  id SERIAL PRIMARY KEY,
  launchpadId VARCHAR(32),
  devName VARCHAR(128) NOT NULL,
  rssi VARCHAR(4),
  isMoving BOOLEAN
);

CREATE TABLE sensorData (
  id SERIAL PRIMARY KEY,
  devName VARCHAR(128) NOT NULL,
  x_acc VARCHAR(16),
  y_acc VARCHAR(16),
  z_acc VARCHAR(16)
);
