CREATE DATABASE rings_boxeo;
USE rings_boxeo;

CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50),
  email VARCHAR(100),
  password VARCHAR(255)
);

CREATE TABLE rings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50),
  descripcion TEXT,
  precio INT,
  imagen VARCHAR(100)
);

CREATE TABLE reservas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT,
  id_ring INT,
  fecha DATE,
  hora INT,
  UNIQUE (id_ring, fecha, hora)
);

INSERT INTO rings (nombre, descripcion, precio, imagen) VALUES
('Ring Profesional', 'Ring oficial para competiciones', 25, 'ring1.jpg'),
('Ring Entrenamiento', 'Ring para entrenamientos', 15, 'ring2.jpg');


CREATE USER "daniel"@"localhost" IDENTIFIED BY "Dani12345&";
GRANT ALL PRIVILEGES ON *.* TO "daniel"@"localhost";
FLUSH PRIVILEGES;
