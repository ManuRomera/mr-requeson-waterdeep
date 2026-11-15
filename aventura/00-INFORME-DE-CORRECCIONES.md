# Informe de correcciones · Ratover: Requesón en Waterdeep

Documento de trabajo para el autor. No forma parte del texto publicable.

## Problemas encontrados y cómo se resuelven

### Estructura y motor de la partida

| # | Problema | Solución en la aventura corregida |
|---|---|---|
| 1 | Sandbox de nueve puertas sin motor: nada empuja a la mesa y todo depende de que el DJ "dé un empujón". | Cuatro frentes con reloj de cuatro pasos y una regla motor: cada escena que el grupo pasa en un sitio, todos los frentes que no están allí avanzan un paso. |
| 2 | Ocho facciones, cinco relojes (Ritual, Princesa, Fama, Comitiva, limpieza) y un coste de viaje que se solapaba con todos. | Cuatro frentes: Rastro Dorado, Sindicato, Rat Tyson, Acreedores. Fama y Comitiva se eliminan. El coste de viaje desaparece: cada escena ya cuesta. La Presión de Princesa queda como reloj local del Baño. |
| 3 | Nueve localizaciones obligadas a competir; la partida real dura seis. | Se juegan seis escenas (Villa, dos nodos, Ático, Baño, Molino). Las nueve existen en el libro. Hay una tabla "qué da cada escena" para que cualquier pareja de nodos baste. |
| 4 | "Fracaso con avance" escrito nueve veces, con listas distintas. | Una sola tabla d6 (tiempo, ruido, deuda, herida, testigo, enemigo). Cada escena solo indica qué se juega. |
| 5 | Cinco copias de la cronología y referencias a "pasos 8 a 12", "15 y 16", "17", "21 y 22" de una lista que no estaba numerada y que decía tener doce. | Una única cronología canónica, numerada del 1 al 14, con la hora de cada contacto con la pulsera. Las escenas remiten al número. |
| 6 | "La jarra se contaminó dos veces" en la introducción, cinco acciones en la cronología. | Cinco acciones simultáneas, en todas partes. |

### Motivación y mecánica

| # | Problema | Solución |
|---|---|---|
| 7 | El ritual solo condenaba a Nixyus. Los PJ no tenían motivo para no vender la pulsera. | La lista del ritual nombra a los cinco PJ con la hora de cada contacto. Destruir la pulsera es supervivencia. Venderla no borra la lista. El Sindicato ignora el ritual. |
| 8 | Los secretos "Lo que temes haber hecho" no hacían nada en mesa. | Confesión con precio: leerlo en voz alta da una relanzada o quita una condición, y marca Culpa. La Culpa decide el epílogo de cada PJ. |
| 9 | Cinco jugadores pasivos que reciben recuerdos del DJ. | Resaca narrativa: el jugador declara algo que hizo anoche, es cierto automáticamente y se paga con un frente, una condición o Culpa. El flashback personal desaparece porque esto lo hace mejor. |
| 10 | Ningún PJ quería algo propio. Todos dependían del contrato social con el máster. | Cada ficha lleva un Deseo propio con su recompensa en el epílogo. |
| 11 | Fichas con ARM, habilidades solapadas o poco útiles, el Guapo hablando del ritual y el Dentista explicando con exactitud los efectos del sedante. | PIPS en lugar de ARM (la armadura es un objeto). Una habilidad útil y única por PJ. El Guapo solo sabe que la joya es de los Gralhund. El Dentista conoce la etiqueta, no las consecuencias. |
| 12 | Inventarios que no cuadraban con la rejilla (el Colgado no podía llevar RESACA con maza y peto). | Cada ficha trae dónde lleva cada cosa y cuadra con Preparado, Portado y Equipaje. |
| 13 | El minijuego El Parmesano Ruso: reglas contradictorias (Bruno "no tira" y a la vez tiran sus dados), ARDIDO te sacaba del juego. | Reglas por estado (quesos que quedan y picantes que quedan), cortesía de la casa, tiradas de Bruno ocultas, ARDIDO sin dejar KO, Bruno solo se retira si quedan únicamente quesos adulterados. |
| 14 | La mano del Dado dependía de adivinar reglas inexistentes. | Se lee la mesa (cuatro observaciones dan ventaja) y se apuesta algo que duela. |

### Incoherencias de historia

| # | Problema | Solución |
|---|---|---|
| 15 | El collar R. T. aparecía en la Villa, lo que regalaba a Tyson antes de tiempo. | El collar solo se encuentra dentro del Baño. En la Villa queda la llave y el pelo blanco, que apuntan a Tyson pero no dicen qué lleva la comadreja. |
| 16 | En el Dado, la botella "que se llevaron" estaba además detrás de la barra. | Solo queda un resto de cinta. |
| 17 | La llave del Dado abría la placa del molino y también una rejilla del Baño sin que ninguna escena lo explicase. | La llave abre solo la placa. La rejilla del Baño la conoce Pazos. |
| 18 | Tyson aparecía como "ratón enorme" y como rata. | Es una rata, en texto, ficha y prompt. |
| 19 | Dos escenas decían ser "la mejor ocasión" para dar la revelación B (Bulevar y Ático). | B solo la da Tyson. El Bulevar da el rastro "animal blanco" y nada más. |
| 20 | Pazos "ratón" en el texto y "rata" en el prompt de imagen. | Ratón. Hay que corregir el prompt del token en el manifiesto. |
| 21 | Plazos temporales sin eje: mediodía, media mañana, amanecer, nivel 3, etc. | El tiempo narrativo lo marcan los frentes. El mediodía es el plazo de Tyson y la media mañana el de la reserva. |
| 22 | La Villa era a la vez una escena de apertura y la escena 1 del sandbox, con dos paneles duplicados. | Una sola escena de apertura que contiene el despertar, la llamada y la Villa abierta. |
| 23 | Express usaba Fama, Comitiva y los seis niveles del ritual. | Express usa Tyson y el Rastro Dorado en tres golpes. |

### Detalles de oficio

- Se retiran las rayas largas como incisos. Se usan comas, dos puntos y paréntesis.
- Se retiran las notas del tipo "esto es importante" dirigidas al autor y las referencias a versiones previas.
- Paper Bird siempre en inglés.
- Los prompts de imagen no se repiten en el libro: viven en `asset-manifest.json`.

## Decisiones tomadas que conviene que revises

1. **"Sube" en el frente de Tyson.** Respeto tu etiqueta, pero Tyson vive en la planta alta y la Villa está en el suelo, así que su movimiento es hacia abajo. Lo describo como "sube el tono" y lo dejo con tu nombre. Si prefieres "Baja", es un cambio de una palabra.
2. **Quién está presente en cada sitio.** Para que la regla motor funcione con seis escenas, el Rastro Dorado se considera presente donde está la pulsera (Villa, Baño, Molino). La apertura no avanza frentes. Con dos nodos y el Ático, el Rastro llega al paso 3 justo al entrar en el Baño. Un tercer nodo lo lleva a la lista. Esto está calculado y explicado en la sección de frentes.
3. **El clímax no tiene ticks automáticos.** Los frentes que hayan llegado al paso 3 irrumpen en la primera ronda. El Rastro marca su paso 4 al terminar la tercera ronda si la pulsera sigue entera.
4. **Culpa.** Cada PJ marca de 0 a 3. Cada nivel tiene un epílogo. Cumplir tu Deseo quita 1.
5. **Los cinco Deseos** son míos. Cámbialos sin miramientos si no encajan con lo que querías.
6. **Armaduras.** El chaleco de contable y las vendas con plomo se asumen 1x1, y el peto de chapa de lata 1x2, según PASO-0.
7. **Resaca narrativa limitada** a una declaración por escena para toda la mesa y como máximo dos por jugador. Sin límite, se come la partida.
8. **Express** se mantiene como apéndice corto.
