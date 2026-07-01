import json
from datetime import datetime
from urllib import error, request

from flask import current_app

from app.models.document import Document, MedicalRecommendation
from app.models.medication import Medication
from app.models.message import Message
from app.models.symptom import VitalSign


def _format_vitals(patient_id):
    vitals = VitalSign.query.filter_by(patient_id=patient_id).order_by(VitalSign.measurement_date.desc()).limit(6).all()
    if not vitals:
        return "Nu exista masuratori inregistrate."

    items = []
    for vital in vitals:
        parts = [vital.measurement_date.strftime('%d.%m.%Y %H:%M')]
        if vital.weight_kg is not None:
            parts.append(f"greutate {vital.weight_kg} kg")
        if vital.systolic_bp is not None and vital.diastolic_bp is not None:
            parts.append(f"TA {vital.systolic_bp}/{vital.diastolic_bp} mmHg")
        if vital.blood_glucose_mg_dl is not None:
            parts.append(f"glicemie {vital.blood_glucose_mg_dl} mg/dL")
        if vital.notes:
            parts.append(f"note: {vital.notes[:120]}")
        items.append("; ".join(parts))
    return "\n".join(f"- {item}" for item in items)


def _format_documents(patient_id):
    documents = Document.query.filter_by(patient_id=patient_id).order_by(Document.uploaded_at.desc()).limit(6).all()
    if not documents:
        return "Nu exista documente incarcate."

    return "\n".join(
        f"- {doc.file_name} | tip: {doc.document_type or '-'} | data upload: {doc.uploaded_at.strftime('%d.%m.%Y %H:%M')}"
        for doc in documents
    )


def _format_recommendations(patient_id):
    recommendations = MedicalRecommendation.query.filter_by(patient_id=patient_id).order_by(MedicalRecommendation.created_at.desc()).limit(6).all()
    if not recommendations:
        return "Nu exista recomandari."

    return "\n".join(
        f"- {rec.title}: {rec.description[:220]} | interval: {rec.start_date.strftime('%d.%m.%Y')} - {rec.end_date.strftime('%d.%m.%Y')}"
        for rec in recommendations
    )


def _format_medications(patient_id):
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).order_by(Medication.created_at.desc()).limit(6).all()
    if not medications:
        return "Nu exista medicatie activa."

    return "\n".join(
        f"- {med.name} | doza: {med.dosage or '-'} | frecventa: {med.frequency or '-'} | instructiuni: {(med.instructions or '-')[:160]} | interval: {med.start_date.strftime('%d.%m.%Y')} - {(med.end_date.strftime('%d.%m.%Y') if med.end_date else '-')}"
        for med in medications
    )


def _format_messages(current_user_id, doctor_user_id):
    if not doctor_user_id:
        return "Pacienta nu are medic asociat si nu exista conversatie medicala activa."

    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.recipient_id == doctor_user_id))
        | ((Message.sender_id == doctor_user_id) & (Message.recipient_id == current_user_id))
    ).order_by(Message.sent_at.desc()).limit(8).all()

    if not messages:
        return "Nu exista mesaje schimbate cu medicul."

    formatted = []
    for msg in reversed(messages):
        speaker = "pacienta" if msg.sender_id == current_user_id else "medicul"
        formatted.append(f"- {speaker}, {msg.sent_at.strftime('%d.%m.%Y %H:%M')}: {msg.content[:220]}")
    return "\n".join(formatted)


def build_patient_context(user):
    patient = user.patient_profile
    if not patient:
        return "Nu exista profil medical complet pentru aceasta utilizatoare."

    pregnancy_info = patient.calculate_pregnancy_week()
    pregnancy_text = (
        f"saptamana {pregnancy_info[0]}, ziua {pregnancy_info[1]}"
        if pregnancy_info else
        "saptamana de sarcina necunoscuta"
    )
    doctor = patient.associated_doctor
    doctor_name = (
        f"Dr. {doctor.user.first_name} {doctor.user.last_name}, {doctor.specialization or 'specializare nespecificata'}"
        if doctor and doctor.user else
        "fara medic asociat"
    )

    profile_lines = [
        f"Pacienta: {user.first_name} {user.last_name}",
        f"Sarcina: {pregnancy_text}",
        f"DUM: {patient.lmp_date.strftime('%d.%m.%Y') if patient.lmp_date else '-'}",
        f"DPN: {patient.due_date.strftime('%d.%m.%Y') if patient.due_date else '-'}",
        f"Tip sarcina: {patient.pregnancy_type or '-'}",
        f"Grupa sanguina: {(patient.blood_type or '-') + ' ' + (patient.rh_factor or '')}".strip(),
        f"Alergii: {patient.allergies or '-'}",
        f"Afectiuni cronice: {patient.chronic_conditions or '-'}",
        f"Tratament permanent declarat: {patient.permanent_medication or '-'}",
        f"Istoric chirurgical: {patient.surgical_history or '-'}",
        f"Medic asociat: {doctor_name}",
    ]

    return "\n".join([
        "DATE PACIENTA",
        "\n".join(profile_lines),
        "",
        "MASURATORI RECENTE",
        _format_vitals(patient.id),
        "",
        "DOCUMENTE",
        _format_documents(patient.id),
        "",
        "RECOMANDARI",
        _format_recommendations(patient.id),
        "",
        "MEDICATIE",
        _format_medications(patient.id),
        "",
        "MESAGERIE RECENTA",
        _format_messages(user.id, doctor.user_id if doctor else None),
    ])


def chat_with_openai(user, user_message, conversation_messages):
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY nu este configurat.')

    patient_context = build_patient_context(user)
    model = current_app.config.get('OPENAI_MODEL', 'gpt-4.1-mini')
    system_prompt = (
        "Esti un medic virtual de suport pentru o gravida care foloseste aplicatia. "
        "Raspunzi clar, calm, in limba romana, folosind cu prioritate datele reale din aplicatie. "
        "Nu inventa date. Daca informatia lipseste, spune explicit asta. "
        "Nu inlocuiesti consultul medical. Pentru simptome severe, urgente, sangerare, durere intensa, lipsa miscari fetale, febra mare, hipertensiune severa sau orice situatie potential periculoasa, spune clar sa contacteze imediat medicul sau serviciile de urgenta. "
        "Daca intrebarea este prea personala, sensibila, necesita decizie clinica individuala, interpretare ferma a documentelor sau depaseste ce poti spune responsabil pe baza datelor disponibile, indruma pacienta sa discute direct cu medicul ei. "
        "Bazeaza raspunsul pe acest context al pacientei:\n"
        f"{patient_context}"
    )

    conversation_text = []
    for item in conversation_messages[-8:]:
        role = item.get('role', 'user')
        content = (item.get('content') or '').strip()
        if content:
            conversation_text.append(f"{role}: {content}")

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": "Istoric recent al conversatiei:\n"
                    + ("\n".join(conversation_text) if conversation_text else "Nu exista mesaje anterioare.")
                    + f"\n\nIntrebarea curenta a pacientei: {user_message}",
                }],
            },
        ],
        "temperature": 0.4,
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI API error: {detail or exc.reason}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Nu s-a putut contacta serviciul OpenAI: {exc.reason}") from exc

    answer = raw.get("output_text", "").strip()
    if answer:
        return answer

    output = raw.get("output", [])
    for item in output:
        for content in item.get("content", []):
            text_value = content.get("text")
            if text_value:
                return text_value.strip()

    raise RuntimeError("OpenAI nu a returnat un raspuns utilizabil.")
