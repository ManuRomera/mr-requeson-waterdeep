# Cambios

## 1.0.0

- **Aspecto de la partida.** Piel de Requesón para las fichas, las tarjetas de tirada y los diálogos de tirada de Mausritter, con versión oscura para MR- Mausritter en español y opción de apagarla. Las ventanas del módulo y las tarjetas de chat estrenan identidad (Cinzel Decorative, Crimson, ciruela y oro), arte en el chat y lupa al pasar el cursor.
- **Ficha esencial.** El cuadro de cada protagonista muestra lema, habilidad y deseo; el texto completo está en Notas. Los PNJ muestran su texto en Notas.
- **Ventanas que caben en cualquier pantalla.** Escala proporcional, scroll interno, botón siempre a la vista y ajuste «Tamaño de las ventanas».
- **Banda sonora con licencia.** Los 10 temas de escena y los 21 ambientes son de Kevin MacLeod (CC BY 4.0) montados con un master común y bucles cortados a compás. Los efectos son ahora grabaciones CC0 de Freesound: 16 en total (timbre de recepción, fichas, ruleta, sello, máquina de escribir, granos de café, saco de boxeo, goteo, cadena, campana, carrito de la limpieza, puerta, tubería...). Créditos en NOTICE, en cada lista, en cada sonido y en el diario «Música y créditos».
- **MR- Dirección por escena.** Cada escena lleva solo sus efectos y sus 4 o 5 ambientes. La barra conserva únicamente dos efectos globales.
- **Portada del módulo y del mundo.** Portada propia, icono y miniaturas; al entrar el GM en un mundo sin fondo ni descripción se pone la portada y la sinopsis. Banner nuevo del README con el logo MR.

## 0.9.0

- **21 ambientes por estado de ánimo** (antes 8), todos de Kevin MacLeod: misterio, miedo, miedo cómico, acción, melancolía, romance, magia y ritual, calma y descanso, jefe final, victoria, derrota, taberna y plan chapuza, además de investigación, comedia caótica, tensión del ritual, sigilo, persecución, combate, revelación y triunfo agridulce.
- **Cambiar Ambiente**: nueva herramienta del GM (y macro) que cambia la música con un fundido sin salir de la escena, o vuelve a la de la escena.
- Los 21 ambientes aparecen como motivos en MR- Dirección. La música de escena entra con fundido.

## 0.8.0

- **Música nueva.** Se sustituye la música sintetizada por 18 pistas de Kevin MacLeod (CC BY 4.0) elegidas por tono y tempo para cada escena y cada ambiente: laúd y guitarra para la portada, un vals cómico para la Capilla, una marcha burocrática para la Notaría, sigilo con oboe para el Bulevar, tensión de cuerdas y percusión para el Ático y acción oscura para la Mandíbula Negra. Bucles sin corte a -26 LUFS. Créditos en `NOTICE.md`.

## 0.7.1

- Corrección: el manifiesto de la 0.7.0 apuntaba al zip de la 0.6.1. La dirección de descarga ahora se calcula sola desde la versión.

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
