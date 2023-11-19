# CONFIGURACION DE COLORES

colors_sentiment = {
    "negative_1": "#e7664c",
	"neutral_1": "#2261aa",
	"positive_1": "#54b399"
 }

amarillo = "#FFFF00"
rosa = "#e926b0"
gris = "#7a9c7d"
verde = "#00FF00"
violeta = "#473b9e"
azul = "#0000ff"
rojo= "#FF0000"

colors_emotions_6 = {
    "anger_2": rojo,
    "fear_2": azul,
    "joy_2":amarillo,
    "love_2":verde,
    "sadness_2": azul,
    "surprise_2":amarillo
    }

azul_miedo_desagrado = "#473b9e"
rosa_aversion_duda = "#ea76e5"
rojo_tension_entusiasmo = "#901f31"
amarillo_satisfaccion_valor = "#d5d432"
verde_altivez_deseo = "#9cf581"
verde_amor_certeza = "#4bb710"
celeste_calma_aburrimiento = "#80c0ea"
celeste_apatia_tristeza = "#53b7d9"

colors_emotions_28 = {
    "neutral_3": celeste_calma_aburrimiento,
    "approval_3": amarillo_satisfaccion_valor,
    "realization_3": amarillo_satisfaccion_valor,
    "caring_3": verde_amor_certeza,
    "curiosity_3": rosa_aversion_duda,
    "confusion_3": rosa_aversion_duda,
    "disapproval_3": celeste_apatia_tristeza,
    "desire_3": verde_altivez_deseo,
    "annoyance_3": celeste_calma_aburrimiento,
    "gratitude_3": amarillo_satisfaccion_valor,
    "excitement_3": rojo_tension_entusiasmo,
    "pride_3": verde_altivez_deseo,
    "remorse_3": celeste_apatia_tristeza,
    "disappointment_3": celeste_apatia_tristeza,
    "relief_3": celeste_calma_aburrimiento,
    "admiration_3": verde_altivez_deseo,
    "anger_3": rojo_tension_entusiasmo,
    "amusement_3": amarillo_satisfaccion_valor,
    "embarrassment_3": azul_miedo_desagrado,
    "joy_3": verde_altivez_deseo,
    "surprise_3": rojo_tension_entusiasmo,
    "nervousness_3": rojo_tension_entusiasmo,
    "love_3": verde_amor_certeza,
    "sadness_3": celeste_apatia_tristeza,
    "grief_3": rosa_aversion_duda,
    "disgust_3": azul_miedo_desagrado,
    "optimism_3": verde_altivez_deseo,
    "fear_3": azul_miedo_desagrado}

colores = colors_sentiment | colors_emotions_6 | colors_emotions_28

if False:
    print("colores modelos M1, M2, M3:", colores)