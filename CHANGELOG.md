# Cambios

## 0.7.0

- **Integración opcional con MR- Dirección.** Si está activo, recibe un paquete con las 10 escenas (lectura, música, figuras y perspectiva), 8 motivos, 6 efectos y los relojes de los cuatro frentes y de la Presión de Princesa. Sin Dirección, el módulo funciona igual. Se recomienda en el manifiesto, no se exige.
- **Fichas de cuerpo entero sin fondo.** Las 22 fichas usan una figura de cuerpo entero con los pies sobre la línea de suelo, lista para Dirección. Ajuste de mundo para volver al token redondo clásico.
- **Efectos.** Sonido y destello al avanzar el ritual, ceder la tubería, tirar Tyson la puerta o quemar el queso. Se activan y se regulan en los ajustes, y los destellos respetan la preferencia de movimiento reducido del sistema.
- **Accesibilidad.** Etiquetas y estados para lectores de pantalla en todas las ventanas, foco visible, objetivos de pulsación mayores, texto grande y alto contraste opcionales.
- **Memoria de ventanas:** cada ventana se reabre donde se dejó.

## 0.6.1

- Las acciones que los jugadores piden al GM (Resaca, Confesión, Culpa, Pizarra, Presión, Parmesano) se ejecutan de una en una. Antes, dos peticiones simultáneas se pisaban y se perdían puntos de Culpa y contadores de límites.
- Probado con un GM y una jugadora a la vez en Foundry 13.351.

## 0.6.0

- Arte completo: 10 escenas, 22 tokens (con token redondo), 15 retratos, 41 objetos, 6 condiciones, 12 documentos, 15 fotografías y 15 iconos, generados con Codex y firmados con la marca MR.
- Miniatura de cada escena y tile animado de la marca MR en cada una.

## 0.5.0

- Banda sonora propia sintetizada (`tools/audio.py`): 10 pistas de escena, 8 ambientes por motivo y 6 efectos. Bucles de 130 a 140 s sin costura, Ogg Opus, -26 LUFS (efectos a -20).
- Tres listas de reproducción en el pack. Cada escena arranca su música al activarse.
- Los prompts de Suno siguen en `asset-manifest.json`: una pista de Suno con el mismo nombre sustituye a la sintetizada sin tocar nada más.

## 0.4.0

- Once macros de mesa, con la lógica en `game.modules.get("mr-requeson-waterdeep").api`: Configuración Inicial, Avanzar a Escena, Mostrar Handout, Panel de Frentes, Pizarra de Investigación, Resaca Narrativa, El Parmesano Ruso, Presión de Princesa, Fichas Confidenciales, Contador de Culpa y Tirada en Tabla.
- Grupo de herramientas «Requesón en Waterdeep» en la barra de escena: los jugadores usan Pizarra, Resaca Narrativa y Contador de Culpa sin permiso de macros.
- Estado de la partida (frentes, presión, culpa, pizarra, parmesano) guardado en el mundo y compartido por socket.

## 0.3.0

- 10 escenas a pantalla completa (sin rejilla, sin niebla), cada una enlazada a su diario.
- 38 diarios: dirección, nueve localizaciones, cinco fichas confidenciales, doce handouts, acuerdo de mesa y las quince fotografías de la noche.
- 8 tablas: los siete d6/d8/d10 de la aventura y la reacción de los fieles de Chispa.
- Todo el contenido sale de `aventura/*.md` con `python3 tools/build_datos.py`.

## 0.2.0

- Pack «MR- Requesón en Waterdeep» (Adventure) con 22 actores (5 PJ, 10 PNJ, 7 genéricos) y 48 objetos, generado con el esquema de Mausritter 0.6.1.
- Inventario de cada PJ colocado en Preparado, Portado y Equipaje.
- Control de zonas: la pulsera y las condiciones no se pueden dejar en el equipaje.
- Ficha del Colgado corregida (una casilla de equipaje sobraba).

## 0.1.0

- Esqueleto del módulo: `module.json` (Foundry 13, Mausritter 0.6.1), idioma español, estilos, carpetas de assets y placeholders por tipo.
- `asset-manifest.json` con rutas y prompts de todos los assets.
- Verificador de assets (`tools/verify_assets.py` y API en Foundry).
- Texto de la aventura corregida en `aventura/`.
