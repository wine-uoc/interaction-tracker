CREATE TABLE cc2640data (
  time BIGINT,
  scanDevice VARCHAR(32) NOT NULL,
  advDevice VARCHAR(128) NOT NULL,
  advDeviceRSSI VARCHAR(4) NOT NULL,
  PRIMARY KEY (time, scanDevice, advDevice)
);

CREATE TABLE phonesdata (
  time BIGINT,
  scanDevice VARCHAR(32) NOT NULL,
  advDevice VARCHAR(32) NOT NULL,
  advDeviceRSSI VARCHAR(4) NOT NULL,
  PRIMARY KEY (time, scanDevice, advDevice)
);

CREATE TABLE audiodata (
  time BIGINT,
  recorderDevice VARCHAR(32) NOT NULL,
  audioData VARCHAR,
  PRIMARY KEY (time, recorderDevice, audioData)
);

-- Entrar en postgres por terminal:
-- -abrir terminal
-- -sudo -u postgres psql
-- \c tracker
-- \d (lista las tablas que hay)
-- hacer consultas, modif, inserts...
--
--


