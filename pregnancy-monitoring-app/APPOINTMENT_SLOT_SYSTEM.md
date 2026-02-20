# Sistem de Programare pe Sloturi Disponibile

## Rezumat

Sistemul de programare a fost complet restructurat pentru a utiliza **sloturi disponibile** în loc de introducere manuală a datelor și orei. Aceasta rezolvă problema "This field is required" și oferă o experiență mai bună pentru utilizatori.

## Probleme Rezolvate

1. ✅ **"This field is required" la fields ora de început și sfârşit**
   - Anteriormente: utilizatorul trebuia să introducă manual data și ora
   - Acum: utilizatorul selectează dintr-o listă de sloturi disponibile generate de sistem

2. ✅ **Validare automată a disponibilității medicului**
   - Sistemul nu mai permite suprapunerea programărilor
   - Sistemul verifică și perioadele de indisponibilitate

3. ✅ **Interfață intuitivă**
   - Calendar cu sloturi disponibile colorat
   - Selecție simplă cu un clic

## Fluxul Mare de Utilizare

### Pentru PACIENTĂ:

```
1. Accesează "Programări" > "Nouă Programare"
   ↓
2. Selectează medicul și data dorite
   ↓
3. Vizualizează sloturi disponibile pe calendar
   ↓
4. Selectează un slot (ex. 09:00-09:30)
   ↓
5. Adaugă note (opțional)
   ↓
6. Confirmă programarea
   ↓
7. Primește confirmare: "Cererea de programare a fost trimisă"
   ↓
8. Așteptă confirmarea din partea medicului
   ↓
9. Status: solicitată → confirmată/respinsă/anulată
```

### Pentru MEDIC:

```
1. Editează profil pentru a seta:
   - Ora de început (default: 9:00)
   - Ora de sfârşit (default: 17:00)
   - Durata slotului (default: 30 minute)
   - Zile lucru (default: luni-vineri)
   ↓
2. Vizualizează cereri de programare în "Programări"
   ↓
3. Confirmă sau respinge cererea
   ↓
4. Pacientă primește notificare
```

## Componente Implementate

### 1. Model: AppointmentSlot (`app/models/appointment.py`)

**Metode principale:**
- `generate_slots_for_doctor(doctor_id, start_date, end_date)` - Generează sloturi disponibile
- `get_available_slots(doctor_id, start_date, end_date)` - Obține sloturi pentru o perioadă

**Logica:**
- Iterează prin fiecare zi din perioada solicitată
- Verifică dacă sunt zile de lucru (Mon-Fri) și doctor e disponibil
- Generează sloturi din `work_start_hour` la `work_end_hour` cu durata de `slot_duration_minutes`
- Exclude sloturi deja rezervate (status CONFIRMED sau REQUESTED)

### 2. Rute pentru Pacientă (`app/routes/patient_routes.py`)

#### Route 1: `/patient/appointments/new` (GET/POST)
- **Formular:** `SelectDoctorAndDateForm`
- **Aceasta:** Selectare medic și dată
- **Output:** Redirecționează la pagina de sloturi

#### Route 2: `/patient/appointments/slots/<doctor_id>` (GET)
- **Parametru query:** `date=YYYY-MM-DD`
- **Aceasta:** Afișează calendarul cu sloturi disponibile
- **Validări:** 
  - Data nu e în trecut
  - Medic și data sunt valide
- **Output:** Template cu sloturi disponibile

#### Route 3: `/patient/appointments/confirm-slot` (POST)
- **Parametri:** `slot_start`, `slot_end`, `doctor_id`, `notes`
- **Aceasta:** Confirmă și crează programarea
- **Validări:**
  - Slot e încă disponibil
  - Doctor e disponibil în perioada respectivă
- **Output:** Redirecționează la lista de programări cu mesaj de succes

### 3. Formulare (`app/forms/patient_forms.py`)

#### SelectDoctorAndDateForm
```python
doctor_id: SelectField      # Medic
appointment_date: DateField # Data programării
```

#### AppointmentSlotSelectionForm
```python
slot_start: HiddenField  # Generator de sistem
slot_end: HiddenField    # Generator de sistem
notes: TextAreaField     # Note pacientă
```

### 4. Template-uri

#### `patient/request_appointment.html`
- Formular pentru selectare medic și dată
- Design modern cu card Bootstrap

#### `patient/appointment_slots.html`
- Afișează info doctor și data selectată
- Calendar interactiv cu sloturi
- Selectare slot și adăugare note
- Validare JavaScript pentru selecție slot
- Buton "Confirmă Programare"

### 5. Update: Profil Doctor

- **Formular:** `DoctorProfileForm` - Adăugat `slot_duration_minutes`
- **Rută:** `/doctor/profile/edit`
- **Funcționalitate:** Doctor poate edita:
  - Ora de început (default: 9)
  - Ora de sfârşit (default: 17)
  - **Durata slotului** (default: 30 minute) ← NOU!

## Dependințe de Bază de Date

Tabelele existente sunt suficiente:
- `appointments` - Stochează programările cu status
- `doctors` - Conține `work_start_hour`, `work_end_hour`, `slot_duration_minutes`
- `doctor_unavailability` - Perioadele când doctorul nu e disponibil

**Nu e necesară migrație nouă** dacă coloanele sunt deja în bază.

## Status Programări

Sistemul suportă 5 stări:

| Status | Descriere | Icon |
|--------|-----------|------|
| `requested` | Solicitată - așteptare confirmare | ⏳ |
| `confirmed` | Confirmată de medic | ✓ |
| `rejected` | Respinsă de medic | ✗ |
| `cancelled` | Anulată | ✗ |
| `completed` | Realizată | ✓ |

## Exemplu de Utilizare

### Pas 1: Doctor setCează availability
1. Accesează `/doctor/profile/edit`
2. Completează:
   - Ora început: 9
   - Ora sfârşit: 17
   - Durata slot: 30
3. Salvează

### Pas 2: Pacientă cere programare
1. Accesează `/patient/appointments/new`
2. Selectează "Dr. X" și "2026-02-15"
3. Vede sloturi disponibile:
   - 09:00-09:30 ✓
   - 09:30-10:00 ✓
   - 10:00-10:30 ✗ (já ocupat)
   - 10:30-11:00 ✓
4. Selectează 09:00-09:30
5. Confirmă

### Pas 3: Doctor confirmă
1. Vede cererea în `/doctor/appointments`
2. Confirmă sau respinge
3. Pacientă primește notificare

## Validări de Siguritate

✅ Validări implementate:
- Doar pacienți pot cere programări
- Doar medici pot confirma/respinge
- Verificare disponibilitate doctor
- Verificare cheie străină (pacient-doctor)
- Prevenire date în trecut
- Prevenire suprapunere programări

## Notificări

Când pacientă solicită programare:
1. Se crează `Notification` pentru doctor
2. Conponent: `type='appointment'`
3. Informații: date, oră, pacientă

## Layout Interfață

```
┌─────────────────────────────────────┐
│ Programare Consultație pe Sloturi   │
├─────────────────────────────────────┤
│ Dr. John Doe                        │
│ Specializare: Ginecologie           │
│ Data: 15.02.2026                    │
│                                     │
│ Sloturi Disponibile:                │
│ ┌─────────────┐ ┌─────────────┐    │
│ │ 09:00-09:30 │ │ 09:30-10:00 │    │
│ └─────────────┘ └─────────────┘    │
│ ┌─────────────┐ ┌─────────────┐    │
│ │ 10:30-11:00 │ │ 11:00-11:30 │    │
│ └─────────────┘ └─────────────┘    │
│                                     │
│ Note: [Textarea]                    │
│                                     │
│ [✓ Confirmă]  [← Înapoi]           │
└─────────────────────────────────────┘
```

## Migrație de la Sistem Vechi

Dacă aveți programări existente cu status "requested" sau "confirmed", acestea vor continua să funcționeze normal.

## Debugging

### Problem: Nu apar sloturi disponibile
**Soluții:**
1. Verifică `doctor.work_start_hour` și `doctor.work_end_hour`
2. Verifică dacă nu e perioada de indisponibilitate
3. Verifică dacă nu e fin de săptămână

### Problem: Eroare "This field is required"
**Acum E REZOLVATÃ!** Sistemul nu mai folosește input manual.

## Fișiere Modificate

- ✅ `app/models/appointment.py` - Adăugat `AppointmentSlot`
- ✅ `app/forms/patient_forms.py` - Adăugate forme noi
- ✅ `app/forms/medical_forms.py` - Actualizar `DoctorProfileForm`
- ✅ `app/routes/patient_routes.py` - Rute noi pentru sloturi
- ✅ `app/routes/doctor_routes.py` - Update `edit_profile`
- ✅ `app/templates/patient/request_appointment.html` - Template nou
- ✅ `app/templates/patient/appointment_slots.html` - Template interactiv
- ✅ `app/templates/patient/appointments.html` - Status actualizat

## Următorii Pași Opționali

1. **Notificări Email** - Trimite email doctor când pacientă solicită
2. **SMS Reminders** - Reamintire 24h înainte de programare
3. **Sincronizare Calend** - Exportare la Google Calendar
4. **Rapoarte** - Statistici programări per medic/pacientă
5. **Feedback Post-Consul** - Formular evaluare consultație

## Suport

Pentru probleme sau intrebări, consultă documentația en swagger API sau contactează dev team.
