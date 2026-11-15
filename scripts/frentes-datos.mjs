export const FRENTES = [
  { id: "rastro", nombre: "Rastro Dorado", quiere: "Un nombre", pasos: [
    ["Distrito", "El oro adquiere temperatura de piel viva. Un Paper Bird nervioso de Nixyus llega a Rat Vegas. Nada visible fuera."],
    ["Edificio", "El sello Gralhund se proyecta sobre espejos y cubiertos. Un criado humano recorre el edificio preguntando por objetos de oro. Desde ahora, cada escena empieza con un Peligro del edificio."],
    ["Lo ven todos", "Siluetas doradas alrededor de la joya. Todo Rat Vegas ve el sello. Bruno, Tupé, Chispa y los crupieres negocian ya por su nombre, no por dinero."],
    ["La lista", "Se escribe sola la lista de nombres con la hora de cada contacto, los cinco protagonistas incluidos. Lord Edrik tiene ubicación e identidades. Es el fracaso de la misión."] ] },
  { id: "sindicato", nombre: "Sindicato", quiere: "Recuperar y revender", pasos: [
    ["Pregunta", "Alguien pregunta por cinco ratones vestidos de morado."],
    ["Localiza", "Saben que están en la Villa. Un mensajero del Sindicato se deja ver."],
    ["Cobrador", "El cobrador del Sindicato se presenta con su oferta (Follón 10). Si no le han dicho la verdad: que se vayan de Waterdeep hoy."],
    ["Asalto", "Los matones del Sindicato asaltan donde estén, a por la pulsera."] ] },
  { id: "tyson", nombre: "Rat Tyson", quiere: "Su animal, vivo", pasos: [
    ["Pregunta", "Tyson pregunta puerta por puerta por su comadreja."],
    ["Sabe dónde", "Ha atado cabos: Princesa está en la Villa."],
    ["Sube", "Sube el tono. Tyson deja el ático y llama a la puerta de la Villa: «¿Dónde está mi niña?»"],
    ["Tira la puerta", "Tyson echa abajo la puerta del baño y se lleva a Princesa, con la pulsera puesta."] ] },
  { id: "acreedores", nombre: "Acreedores", quiere: "Cobrar", pasos: [
    ["Aviso", "Un chaval del almacén, un mozo del Dado o un cobrador entrega un recado: hay cosas por cobrar."],
    ["Inventario", "Dos cobradores de Bruno empiezan el inventario del embargo en la Villa y en la Manada."],
    ["Embargo", "Embargan un objeto a cada personaje con DEUDA y bloquean un paso de cualquier plan que necesite sus bienes."],
    ["Subasta", "Subastan lo que queda. En el Molino aparecen Bruno, Tupé, Chispa y el clan con papeles y con prisa."] ] }
];

// Frente presente en cada escena: no avanza cuando el grupo está allí.
export const PRESENTES = { "00": [], "01": ["rastro"], "02": ["sindicato"], "03": ["sindicato"], "04": ["acreedores"], "05": ["acreedores"], "06": ["acreedores"], "07": ["tyson"], "08": ["rastro"], "09": ["rastro"] };

export const PRESION = [
  "Sin empezar.",
  "Golpes sordos y arañazos.",
  "La puerta se arquea y asoma una garra.",
  "La grifería chirría al tirar y el charco del suelo empieza a extenderse.",
  "LA TUBERÍA CEDE. La grifería se arranca de la pared, el agua sale a presión y Princesa queda suelta con un trozo de tubo colgando del cuello y la pulsera todavía puesta."
];

export const EPILOGOS = [
  "Nadie sabe lo que hizo. Sale limpio, con una versión de la noche que nadie contradice.",
  "Alguien sospecha. Un PNJ le debe un favor, y le cobrará otro.",
  "La Manada lo sabe. Pasa una temporada pagando un precio en forma de recados, deudas o silencios.",
  "Carga con ello en público. El montaje final desmiente la culpa individual: fueron los cinco. Pero él ya lo ha pagado."
];

export const CONDICIONES_RESACA = ["DEUDA", "BUSCADO", "MORDIDO", "ARDIDO", "COMPROMISO FAMILIAR"];
