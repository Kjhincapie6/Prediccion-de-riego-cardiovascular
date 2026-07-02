if pred == 1:
    st.error("🔴 Alto riesgo cardiovascular")

    st.markdown("---")
    st.subheader("❤️ Recomendaciones Personalizadas")

    recomendaciones = []

    if presion_sistolica >= 140 or presion_diastolica >= 90:
        recomendaciones.append(
            "🩺 **Controle su presión arterial.** Sus valores se encuentran elevados y es recomendable consultar a un profesional de la salud."
        )

    if colesterol_modelo >= 2:
        recomendaciones.append(
            "🥗 **Mejore su alimentación.** Reduzca grasas saturadas y aumente el consumo de frutas, verduras y fibra."
        )

    if glucosa >= 126:
        recomendaciones.append(
            "🍬 **Controle sus niveles de glucosa.** Es recomendable realizar una valoración médica."
        )

    if fuma == 1:
        recomendaciones.append(
            "🚭 **Deje de fumar.** El tabaquismo incrementa significativamente el riesgo cardiovascular."
        )

    if consume_alcohol == 1:
        recomendaciones.append(
            "🍺 **Reduzca el consumo de alcohol.**"
        )

    if actividad_fisica == 0:
        recomendaciones.append(
            "🏃 **Aumente su actividad física.** Se recomienda al menos 150 minutos de ejercicio moderado por semana."
        )

    imc = peso_kg / ((estatura_cm / 100) ** 2)

    if imc >= 25:
        recomendaciones.append(
            f"⚖️ **Su IMC es {imc:.1f}.** Se recomienda trabajar en alcanzar un peso saludable."
        )

    for r in recomendaciones:
        st.write(r)

    st.info(
        "⚠️ Estas recomendaciones son orientativas y no reemplazan la valoración de un profesional de la salud."
    )

else:
    st.success("🟢 Bajo riesgo cardiovascular")
    st.balloons()
    st.info(
        "🎉 El modelo estima un riesgo cardiovascular bajo. Continúe manteniendo hábitos saludables y realice controles médicos periódicos."
    )
