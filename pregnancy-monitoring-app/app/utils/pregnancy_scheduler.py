"""
Scheduler și utility functions pentru generarea automată a task-urilor de sarcină.
"""
from datetime import datetime, date, timedelta
from app import db
from app.models import Patient, PregnancyCalendarTask, PregnancyWeekInfo
import json


# Template de task-uri recomandate pentru fiecare săptămână de sarcină
PREGNANCY_WEEK_TASKS = {
    1: [
        {"title": "Testare RPG", "type": "analysis", "priority": "high"},
        {"title": "Analiza de sânge inițială", "type": "analysis", "priority": "high"},
    ],
    4: [
        {"title": "Prima vizită prenatală", "type": "appointment", "priority": "high"},
        {"title": "Echografie transvaginală", "type": "appointment", "priority": "normal"},
    ],
    8: [
        {"title": "Test quad screening", "type": "analysis", "priority": "normal"},
        {"title": "Review parametri", "type": "appointment", "priority": "normal"},
    ],
    10: [
        {"title": "Consultație nutriționist", "type": "appointment", "priority": "normal"},
        {"title": "Curs pregătire pentru maternitate", "type": "general_task", "priority": "normal"},
    ],
    11: [
        {"title": "Analiza glucozei (OGTT)", "type": "analysis", "priority": "high"},
        {"title": "Screening pentru diabetul gestațional", "type": "analysis", "priority": "high"},
    ],
    13: [
        {"title": "Amniocenteză (dacă e indicată)", "type": "analysis", "priority": "normal"},
        {"title": "Screening ADN fetal", "type": "analysis", "priority": "normal"},
    ],
    15: [
        {"title": "Analiza Rh sensibilizare", "type": "analysis", "priority": "high"},
        {"title": "Consultație prenatală", "type": "appointment", "priority": "normal"},
    ],
    18: [
        {"title": "Analiza pentru defecte de tub neural", "type": "analysis", "priority": "normal"},
        {"title": "Revizuire status sirologic", "type": "analysis", "priority": "normal"},
    ],
    20: [
        {"title": "Ecografie morfologică (20 săpt)", "type": "appointment", "priority": "high"},
        {"title": "Screening pentru anomalii", "type": "appointment", "priority": "high"},
    ],
    24: [
        {"title": "Screening pentru preeclampsie", "type": "analysis", "priority": "high"},
        {"title": "Consultație obstetrician", "type": "appointment", "priority": "normal"},
    ],
    26: [
        {"title": "Testare pentru streptococ B (GBS)", "type": "analysis", "priority": "high"},
        {"title": "Verificare status obstetrical", "type": "appointment", "priority": "normal"},
    ],
    28: [
        {"title": "Verificare tensiune arterială și proteini", "type": "measurement", "priority": "high"},
        {"title": "Consultație pentru birtuirea prematură", "type": "appointment", "priority": "normal"},
    ],
    30: [
        {"title": "Evaluare poziție făt", "type": "appointment", "priority": "normal"},
        {"title": "Discuție plan naștere", "type": "appointment", "priority": "normal"},
    ],
    32: [
        {"title": "Ecografie de control (32 săpt)", "type": "appointment", "priority": "normal"},
        {"title": "Evaluare creștere făt", "type": "appointment", "priority": "normal"},
    ],
    34: [
        {"title": "Verificare poziție și prezentare făt", "type": "appointment", "priority": "high"},
        {"title": "Discuție opțiuni naștere", "type": "appointment", "priority": "normal"},
    ],
    35: [
        {"title": "Consultație finală prenatală", "type": "appointment", "priority": "normal"},
        {"title": "Discuție complicații și semne de alarmă", "type": "appointment", "priority": "normal"},
    ],
    36: [
        {"title": "Evaluare cervicală și statut", "type": "appointment", "priority": "normal"},
        {"title": "Plan de naștere finalizat", "type": "document_upload", "priority": "normal"},
    ],
    37: [
        {"title": "Consultație prenatală săptămânală", "type": "appointment", "priority": "normal"},
        {"title": "Monitorizare NST (non-stress test)", "type": "measurement", "priority": "high"},
    ],
    38: [
        {"title": "Continuare monitorizare săptămânală", "type": "appointment", "priority": "normal"},
        {"title": "Verificare embrioni și parametri", "type": "measurement", "priority": "normal"},
    ],
    39: [
        {"title": "Consultație final prenatală", "type": "appointment", "priority": "high"},
        {"title": "Discuție început travaliu", "type": "appointment", "priority": "high"},
    ],
    40: [
        {"title": "Monitorizare pentru depășire termin", "type": "appointment", "priority": "high"},
        {"title": "Evaluare opțiuni inducere travaliu", "type": "appointment", "priority": "high"},
    ],
}


def generate_initial_pregnancy_tasks(patient_id):
    """
    Generează task-urile inițiale de sarcină pentru o pacientă nouă.
    Aceasta se execută când pacientă completează DUM.
    """
    patient = Patient.query.get(patient_id)
    if not patient or not patient.lmp_date:
        return False
    
    try:
        # Calculează care săptămână de sarcină a trecut deja
        current_week, _ = patient.calculate_pregnancy_week()
        if not current_week:
            return False
        
        # Generează task-uri pentru fiecare săptămână rămase (plus 5 viitoare pentru context)
        for week in range(current_week, min(current_week + 5, 41)):
            if week in PREGNANCY_WEEK_TASKS:
                for task_template in PREGNANCY_WEEK_TASKS[week]:
                    # Calculează data datorată pentru această săptămână
                    due_date = patient.lmp_date + timedelta(weeks=week)
                    
                    # Verifică dacă task-ul nu există deja
                    existing = PregnancyCalendarTask.query.filter_by(
                        patient_id=patient_id,
                        title=task_template['title'],
                        week_number=week
                    ).first()
                    
                    if not existing:
                        task = PregnancyCalendarTask(
                            patient_id=patient_id,
                            title=task_template['title'],
                            description=f"Task recomandat pentru săptămâna {week} de sarcină",
                            task_type=task_template['type'],
                            week_number=week,
                            due_date=due_date,
                            priority=task_template.get('priority', 'normal'),
                            auto_generated=True,
                            send_reminder=True,
                            reminder_days_before=7 if task_template['type'] == 'appointment' else 3
                        )
                        db.session.add(task)
        
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"Eroare la generarea task-urilor: {e}")
        return False


def update_pregnancy_tasks_weekly():
    """
    Task periodic care actualizează task-urile de sarcină.
    Aceasta se execută în fiecare pentru a adăuga task-urile pentru săptămânile noi.
    
    Ar fi trebui apelat dintr-un scheduler (APScheduler sau cron).
    """
    from datetime import datetime
    
    all_patients = Patient.query.filter(Patient.lmp_date != None).all()
    
    for patient in all_patients:
        try:
            current_week, _ = patient.calculate_pregnancy_week()
            if not current_week or current_week > 40:
                continue
            
            # Verifică dacă deja existe task-uri pentru săptămâna curentă
            existing_tasks = PregnancyCalendarTask.query.filter_by(
                patient_id=patient.id,
                week_number=current_week
            ).count()
            
            # Adaugă task-uri pentru următoarele 3 săptămâni dacă nu există
            for offset in range(3):
                week = current_week + offset
                if week > 40:
                    break
                
                if week in PREGNANCY_WEEK_TASKS:
                    for task_template in PREGNANCY_WEEK_TASKS[week]:
                        existing = PregnancyCalendarTask.query.filter_by(
                            patient_id=patient.id,
                            title=task_template['title'],
                            week_number=week
                        ).first()
                        
                        if not existing:
                            due_date = patient.lmp_date + timedelta(weeks=week)
                            task = PregnancyCalendarTask(
                                patient_id=patient.id,
                                title=task_template['title'],
                                description=f"Task recomandat pentru săptămâna {week}",
                                task_type=task_template['type'],
                                week_number=week,
                                due_date=due_date,
                                priority=task_template.get('priority', 'normal'),
                                auto_generated=True,
                                send_reminder=True,
                                reminder_days_before=7 if task_template['type'] == 'appointment' else 3
                            )
                            db.session.add(task)
            
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            print(f"Eroare la update task-uri pentru pacientă {patient.id}: {e}")
            continue


def get_pregnancy_week_info(week_number):
    """
    Returnează informații detaliate pentru o anumită săptămână de sarcină.
    Dacă nu există în BD, returnează info default.
    """
    week_info = PregnancyWeekInfo.query.filter_by(week_number=week_number).first()
    return week_info


def mark_task_completed(task_id, completion_notes=None):
    """
    Marchează un task ca finalizat.
    """
    task = PregnancyCalendarTask.query.get(task_id)
    if task:
        task.is_completed = True
        task.completed_date = datetime.utcnow()
        task.completion_notes = completion_notes
        db.session.commit()
        
        # TODO: Crează notificare pentru doctor dacă e task important
        
        return True
    return False


def get_patient_pending_tasks(patient_id, limit=None):
    """
    Returnează task-urile nesfinalizate ale unei paciente, ordonate după prioritate și dată.
    """
    query = PregnancyCalendarTask.query.filter_by(
        patient_id=patient_id,
        is_completed=False
    ).order_by(
        PregnancyCalendarTask.priority.desc(),
        PregnancyCalendarTask.due_date.asc()
    )
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def seed_pregnancy_week_info():
    """
    Umple BD cu informații pentru fiecare săptămână de sarcină.
    Aceasta se execută o singură dată - la inițializarea BD.
    """
    
    # Template-uri de informații pentru fiecare săptămână
    pregnancy_templates = {
        1: {
            "mom_info": "Menstruația este târziă. S-ar putea să nu vă simțiți gravidă încă.",
            "mom_symptoms": "Niciun simptom vizibil",
            "baby_info": "Ovulul fertilizat se deplasează prin trompă",
            "baby_size_description": "Microscopic - o celulă",
            "baby_weight_grams": 0,
            "baby_length_cm": 0,
            "recommended_tests": "Nici o analiză în această an",
            "warning_signs": "Niciun semn de alarmă specific",
            "nutrition_tips": "Luați acid folic (400-800 mcg/zi)",
            "exercise_tips": "Activitate fizică normală",
            "lifestyle_tips": "Evitați alcoolul și fumatul"
        },
        4: {
            "mom_info": "Ați observat că vi-a lipsit menstruația. Pot apărea mâncărimi și oboseală",
            "mom_symptoms": "Oboseală, mâncărimi, sensibilitate la sâni",
            "baby_info": "Embrionul s-a implantat în uter. Se formează plăcenta",
            "baby_size_description": "Mărimea unei semințe de susan poppy",
            "baby_weight_grams": 1,
            "baby_length_cm": 0.3,
            "recommended_tests": "Test de sarcină confirmat; Prima vizită prenatală",
            "warning_signs": "Sângerare abundentă, durere abdominală severă",
            "nutrition_tips": "Mâncați alimente bogate în fier și calciu",
            "exercise_tips": "Mers ușor, yoga pentru gravide",
            "lifestyle_tips": "Odihnă suficientă, evitați stresul"
        },
        8: {
            "mom_info": "Simțiți mai multă oboseală. Ar putea apărea greață",
            "mom_symptoms": "Greață, oboseală, mâncărimi, dureri de spate ușoare",
            "baby_info": "Cordonul ombilical se formează. Organele majore încep să se dezvolte",
            "baby_size_description": "Mărimea unei fasole",
            "baby_weight_grams": 1,
            "baby_length_cm": 1.6,
            "recommended_tests": "Ecografie transvaginală. Test de sânge pentru sarcini multiple",
            "warning_signs": "Sângerare vaginală, crampe severe",
            "nutrition_tips": "Proteina este esențială. Luați acid folic zilnic",
            "exercise_tips": "Mers, înot, exerciții de flexibilitate",
            "lifestyle_tips": "Evitați temperaturi înalte și stresul"
        },
        12: {
            "mom_info": "Ar putea apărea o ușoară curbă abdominală. Finețe mai redusă",
            "mom_symptoms": "Greață poate să scadă. Oboseală continuă",
            "baby_info": "Unghiile și părul încep să crească. Organele se diferențiază",
            "baby_size_description": "Mărimea unui prune",
            "baby_weight_grams": 14,
            "baby_length_cm": 6,
            "recommended_tests": "Screening trimestrial 1: translucență nucală, beta hCG",
            "warning_signs": "Durere abdominală persistentă, sângerare vaginală",
            "nutrition_tips": "Crești necesarul caloric. Alimente cu calciu și fier",
            "exercise_tips": "Exerciții cu greutate rămasă, dar evitați supraexecuția",
            "lifestyle_tips": "Purtați haine confortabile. Evitați căldura extremă"
        },
        16: {
            "mom_info": "Burta dumneavoastră este vizibil mai mare. Energia revine",
            "mom_symptoms": "Energia crește, greață diminuată, durere de spate",
            "baby_info": "Fătul produciți deja lichid de amniotic. Creșterea accelerează",
            "baby_size_description": "Mărimea unei mere",
            "baby_weight_grams": 100,
            "baby_length_cm": 11,
            "recommended_tests": "Ecografie nivel 2 (morfologie). Test AFP opțional",
            "warning_signs": "Lipsa mișcării fetale, sângerare abundantă",
            "nutrition_tips": "Mai mult fier și proteine. Hidratare bună",
            "exercise_tips": "Mersu ușor și constant. Exerciții prenumere de ton",
            "lifestyle_tips": "Dormiți pe partea stângă. Evitați poziții pe spate"
        },
        20: {
            "mom_info": "Chiar dacă burta se mai vede clar. Picioarele pot să umfle",
            "mom_symptoms": "Durere de spate, crampe, ușor umflat",
            "baby_info": "Fătul poate să vă simțiți mișcările. Structurile încep să se maturizeaze",
            "baby_size_description": "Mărimea unei banane",
            "baby_weight_grams": 300,
            "baby_length_cm": 16,
            "recommended_tests": "Ecografie morfologică detaliată (20 săpt). Screening complet anomalii",
            "warning_signs": "Durere abdominală sau pelvică severă, sângerare vaginală",
            "nutrition_tips": "Calorii suficiente. Alimente moi dacă ai probleme digestive",
            "exercise_tips": "Plimbări regulate. Scufundări în apă caldă",
            "lifestyle_tips": "Evitați căderi. Purtați pantofi confortabili"
        },
        24: {
            "mom_info": "Nausea se dispare. Apare leucoree (secreții vaginale). Creștere poftei de mâncare",
            "mom_symptoms": "Constipație, durere de spate, umflare anginoză",
            "baby_info": "Fătul poate să gesturi în UTC. Creierul se dezvoltă rapid",
            "baby_size_description": "Mărimea unui porumb",
            "baby_weight_grams": 600,
            "baby_length_cm": 21,
            "recommended_tests": "Test pentru diabete gestațional (OGTT). Analiza de sânge rutină",
            "warning_signs": "Glicemie ridicată, vedere încețoșată, umflare excesivă",
            "nutrition_tips": "Evitați zahărul și glucidele simple. ProteINA și fibre",
            "exercise_tips": "Exerciții Kegel. Cersete pentru gravide",
            "lifestyle_tips": "Stinui ridicări grele. Odihnă suficientă"
        },
        28: {
            "mom_info": "Burta este vizibil mai mare. Putți simți Braxton-Hicks (false contracții)",
            "mom_symptoms": "Crampe intermitente, umflare, durere pelvică",
            "baby_info": "Fătul deschide ochii. Creșterea greutății accelerează",
            "baby_size_description": "Mărimea unui ananas",
            "baby_weight_grams": 1000,
            "baby_length_cm": 25,
            "recommended_tests": "Analiza de sânge 2 (hemograma). Screening pentru streptococ B",
            "warning_signs": "Tensiune arterială crescută, viziune incețoșată, durere epigastrică",
            "nutrition_tips": "Calciu și proteINA mai mulți. Apă multă",
            "exercise_tips": "Plimbări scurte. Exerciții de flexibilitate",
            "lifestyle_tips": "Îți face clonoasă pe plăcintă. Evitați poziții pe spate"
        },
        32: {
            "mom_info": "Burta este foarte mare. Respirația poate fi dificilă. Insomnie frecventă",
            "mom_symptoms": "Respirație dificilă, constipație, crampe notturne",
            "baby_info": "Piele este mai netedă. Creșterea continuă",
            "baby_size_description": "Mărimea unui pepene",
            "baby_weight_grams": 1700,
            "baby_length_cm": 28,
            "recommended_tests": "Ecografia de control. Verificare poziție făt",
            "warning_signs": "Sângerare vaginală, durere de spate severă, vertij",
            "nutrition_tips": "Alimentos în porcții mici și frecvente. Evitați cofeina",
            "exercise_tips": "Exerciții ușoare de stretching. Înoț",
            "lifestyle_tips": "Ridicați picioarele asta deasupra inimii. Purtați șosete de compresie"
        },
        36: {
            "mom_info": "Burta a coborât ușor - fătul se poziționează pentru naștere",
            "mom_symptoms": "Durere pelvică, constipație, frecvență urinară crescută",
            "baby_info": "Capul fătului intră în pelvis. Piele este mai rose",
            "baby_size_description": "Mărimea unui pepene gros",
            "baby_weight_grams": 2500,
            "baby_length_cm": 33,
            "recommended_tests": "Ecografia finală. Verificare cephalad",
            "warning_signs": "Durere abdominală persistentă tip contracții, sângerare",
            "nutrition_tips": "Mâncări ușor digerabile. Evitați alimentele grele",
            "exercise_tips": "Mers ușor. Poziții care ușurează presiunea",
            "lifestyle_tips": "Pregătiți-vă pentru travaliu. Lucruri pentru spital"
        },
        40: {
            "mom_info": "Așteptați nașterea iminentă. Frustrări și nervozidate sunt normale",
            "mom_symptoms": "Contracții regulate potențiale fals travaliu",
            "baby_info": "Fătul este complet dezvoltat și gata pentru naștere",
            "baby_size_description": "Mărimea unui pepene gros mare",
            "baby_weight_grams": 3400,
            "baby_length_cm": 36,
            "recommended_tests": "Monitorizare NST (non-stress test) dacă e indicată",
            "warning_signs": "Pierdere lichidu amniotic, sângerare vaginală, durere ritmică",
            "nutrition_tips": "Mâncări foarte ușoare. Rămâneți hidratate",
            "exercise_tips": "Mers pentru a-și accelera travaliul. Poziții confortabile",
            "lifestyle_tips": "Relaxare. Sunați medicul la primele semne de travaliu"
        },
    }
    
    try:
        for week_num, info in pregnancy_templates.items():
            # Verifică dacă săptămâna există deja
            existing = PregnancyWeekInfo.query.filter_by(week_number=week_num).first()
            if not existing:
                week_info = PregnancyWeekInfo(
                    week_number=week_num,
                    mom_info=info.get('mom_info', ''),
                    mom_symptoms=info.get('mom_symptoms', ''),
                    baby_info=info.get('baby_info', ''),
                    baby_size_description=info.get('baby_size_description', ''),
                    baby_weight_grams=info.get('baby_weight_grams', 0),
                    baby_length_cm=info.get('baby_length_cm', 0),
                    recommended_tests=info.get('recommended_tests', ''),
                    warning_signs=info.get('warning_signs', ''),
                    nutrition_tips=info.get('nutrition_tips', ''),
                    exercise_tips=info.get('exercise_tips', ''),
                    lifestyle_tips=info.get('lifestyle_tips', '')
                )
                db.session.add(week_info)
        
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"Eroare la seed-ifying pregnancy week info: {e}")
        return False
