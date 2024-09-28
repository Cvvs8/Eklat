USE eklat_clientes; 

-- Insertar clientes ficticios en la tabla Clientes
INSERT INTO Clientes (nombre_cliente, tipo_identificacion, numero_identificacion, direccion_entrega, ciudad, barrio, telefonos, email, regimen_iva, ordenado_a, ordenado_por)
VALUES 
('Ana Torres', 'Cédula', '1023456789', 'Carrera 15, Bogotá', 'Bogotá', 'Chapinero', '3103456789', 'ana.torres@example.com', 'Simplificado', 'Carlos Ramírez', 'Juan Martínez'),
('Luis Rojas', 'Cédula', '2034567890', 'Avenida 68, Cali', 'Cali', 'San Fernando', '3112345678', 'luis.rojas@example.com', 'Simplificado', 'Marta Rodríguez', 'Laura González'),
('Sofía Gómez', 'Pasaporte', 'A1234567', 'Calle 12, Medellín', 'Medellín', 'El Poblado', '3124567890', 'sofia.gomez@example.com', 'Común', 'Andrés Torres', 'Carlos Pérez'),
('Fernando Suárez', 'Cédula', '3045678901', 'Carrera 10, Barranquilla', 'Barranquilla', 'Centro', '3135678901', 'fernando.suarez@example.com', 'Común', 'Luis González', 'María López'),
('Carolina Pérez', 'Cédula', '4056789012', 'Carrera 30, Cartagena', 'Cartagena', 'Bocagrande', '3146789012', 'carolina.perez@example.com', 'Simplificado', 'Fernando Cruz', 'Pedro Rodríguez');

-- Insertar pedidos para los clientes ficticios en la tabla Pedidos
INSERT INTO Pedidos (cliente_id, nombre_laboratorio, vendedor, codigo_montura, valor_montura, codigo_lente, valor_lente, otros, valor_otros, total_venta, dia_entrega, guia_despacho, observaciones, fecha)
VALUES
(6501, 'Laboratorio A', 'Vendedor 1', 'MONT001', 52000, 'LENTE001', 160000, 'Estuche', 15000, 227000, '2024-10-10', 'G001', 'Pedido urgente', '2024-09-01'),
(6502, 'Laboratorio B', 'Vendedor 2', 'MONT002', 54000, 'LENTE002', 165000, 'Paño', 10000, 229000, '2024-10-12', 'G002', 'Requiere seguimiento', '2024-09-03'),
(6503, 'Laboratorio C', 'Vendedor 3', 'MONT003', 56000, 'LENTE003', 170000, 'Garantía', 20000, 246000, '2024-10-15', 'G003', 'Cliente frecuente', '2024-09-05'),
(6504, 'Laboratorio D', 'Vendedor 4', 'MONT004', 48000, 'LENTE004', 150000, 'Paño', 5000, 203000, '2024-10-18', 'G004', 'Cliente nuevo', '2024-09-07'),
(6505, 'Laboratorio E', 'Vendedor 5', 'MONT005', 50000, 'LENTE005', 155000, 'Estuche', 12000, 217000, '2024-10-20', 'G005', 'Descuento aplicado', '2024-09-09');

-- Insertar detalles de lentes relacionados con los pedidos en la tabla Detalles_Lentes
INSERT INTO Detalles_Lentes (pedido_id, esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi)
VALUES
(6501, '-1.25', '-0.50', 90, '2.50', 32, '-1.50', '-0.75', 180, '2.25', 30),
(6502, '-0.75', '-0.25', 80, '1.75', 31, '-0.50', '-0.50', 170, '2.00', 32),
(6503, '-2.00', '-1.00', 100, '3.00', 34, '-2.25', '-1.25', 190, '2.75', 33),
(6504, '-1.00', '-0.75', 95, '2.00', 30, '-1.25', '-1.00', 185, '2.25', 31),
(6505, '-0.50', '-0.50', 85, '1.50', 33, '-0.75', '-0.25', 175, '1.75', 32);

-- Insertar órdenes de laboratorio relacionadas con los pedidos en la tabla Orden_Laboratorio
INSERT INTO Orden_Laboratorio (pedido_id, montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, fecha_lab, gama_fotocromatico)
VALUES
(6501, 'Montura 1', 'Negro', 'Policarbonato', 'Blue', 'SI', 'Alta', 'SI', 'Tallado', 'SI', 'Invisible', 'AF001', 'Corredor 1', 'Adicional 1', '2024-09-01', 'Gama Alta'),
(6502, 'Montura 2', 'Marrón', 'Orgánico', 'Green', 'NO', '', 'SI', 'Terminado', 'NO', 'Flat Top', 'AF002', 'Corredor 2', 'Adicional 2', '2024-09-03', ''),
(6503, 'Montura 3', 'Azul', 'Policarbonato', 'Block', 'SI', 'Media', 'NO', '', 'SI', 'Invisible', 'AF003', 'Corredor 3', 'Adicional 3', '2024-09-05', 'Gama Media'),
(6504, 'Montura 4', 'Rojo', 'Cristal', 'Blue', 'NO', '', 'SI', 'Extrarrango', 'NO', 'Flat Top', 'AF004', 'Corredor 4', 'Adicional 4', '2024-09-07', ''),
(6505, 'Montura 5', 'Verde', 'Policarbonato', 'Block', 'SI', 'Baja', 'NO', '', 'SI', 'Invisible', 'AF005', 'Corredor 5', 'Adicional 5', '2024-09-09', 'Gama Baja');

-- Insertar pagos relacionados con los pedidos en la tabla Pagos
INSERT INTO Pagos (pedido_id, pago_efectivo, pago_bancolombia, pago_davivienda, pago_redeban, pago_bold, pago_mensajeria_eklat, pago_mercadopago, pago_payco, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro)
VALUES
(6501, 100000, 50000, 0, 50000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(6502, 60000, 0, 60000, 50000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(6503, 70000, 50000, 0, 60000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(6504, 80000, 0, 0, 50000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(6505, 75000, 0, 0, 50000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);


