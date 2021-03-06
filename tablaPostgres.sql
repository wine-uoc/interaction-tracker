CREATE TABLE rssidata (
  id SERIAL PRIMARY KEY,
  launchpadId VARCHAR(32),
  devName VARCHAR(128) NOT NULL,
  rssi VARCHAR(4),
  ustime VARCHAR(16)
);

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
