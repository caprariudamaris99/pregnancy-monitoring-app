# Pregnancy Monitoring App - Aplicație pentru Monitorizarea Sarcinilor

## Descriere Project
Aplicație web pentru monitorizarea sarcinilor, care permite gravidelor să urmărească parametri medicali și medicilor să gestioneze pacientele.

## Stack Tehnologic
- **Backend**: Node.js + Express.js
- **Frontend**: React.js + TypeScript + Tailwind CSS
- **Database**: MongoDB
- **Autentificare**: JWT (JSON Web Tokens)
- **Validare**: Joi
- **Email**: Nodemailer

## Structură Proiect
```
pregnancy-monitoring-app/
├── backend/              # API REST Node.js + Express
├── frontend/             # Aplicație React
├── docs/                 # Documentație și scheme
└── README.md
```

## Funcționalități Principale

### Gravidă (Pacientă)
1. Autentificare și gestionare cont
2. Profil medical și date de sarcină
3. Monitorizare parametri (greutate, tensiune, glicemie)
4. Înregistrare simptome
5. Programare consultații
6. Gestionare medicație
7. Comunicare cu medicul
8. Grafice și trenduri

### Medic
1. Autentificare și profil profesional
2. Gestionare paciente
3. Vizualizare dosare paciente
4. Gestionare disponibilitate și programări
5. Upload documente medicale
6. Mesagerie cu pacientele
7. Recomandări medicale

## Instalare și Rulare

### Backend
```bash
cd backend
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Documentație
Vezi folder `/docs` pentru:
- Diagrama ER (bază de date)
- API Documentation
- User Journey Maps
- Specificații de securitate

---
**Data**: februarie 2026
**Status**: În dezvoltare
