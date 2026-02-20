# Database Schema - MongoDB Collections

## 1. Users Collection
```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "password", "role", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        email: { bsonType: "string", pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" },
        password: { bsonType: "string" }, // hashed
        role: { enum: ["gravida", "medic", "admin"] },
        firstName: { bsonType: "string" },
        lastName: { bsonType: "string" },
        phone: { bsonType: "string" },
        
        // Avatar/Imagine profil
        avatar: { bsonType: "string" },
        
        // Status cont
        verified: { bsonType: "bool" },
        verificationToken: { bsonType: "string" },
        lastLogin: { bsonType: "date" },
        
        // Pentru resetare parolă
        resetPasswordToken: { bsonType: "string" },
        resetPasswordExpires: { bsonType: "date" },
        
        // Consimțământ GDPR
        gdprConsent: { bsonType: "bool" },
        gdprConsentDate: { bsonType: "date" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 2. Gravida (Pregnant Women) Collection
```javascript
db.createCollection("gravidas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" }, // Reference to users collection
        
        // Date sarcină
        DUM: { bsonType: "date" }, // Data ultimei menstruații
        DPN: { bsonType: "date" }, // Data probabilă a nașterii (calculată automat)
        currentPregnancyWeek: { bsonType: "int" },
        currentPregnancyDay: { bsonType: "int" },
        
        // Tip sarcină
        pregnancyType: { enum: ["unica", "multipla"] },
        numberOfFetuses: { bsonType: "int" },
        
        // Date medicale
        bloodType: { bsonType: "string" }, // O, A, B, AB
        rhFactor: { enum: ["positive", "negative"] },
        
        // Istoric medical
        medicalHistory: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              condition: { bsonType: "string" }, // alergii, afecțiuni cronice
              description: { bsonType: "string" },
              startDate: { bsonType: "date" },
              endDate: { bsonType: "date" },
              status: { enum: ["active", "resolved"] }
            }
          }
        },
        
        // Medicație permanentă
        permanentMedication: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              medicament: { bsonType: "string" },
              doza: { bsonType: "string" },
              frecventa: { bsonType: "string" },
              startDate: { bsonType: "date" },
              indication: { bsonType: "string" }
            }
          }
        },
        
        // Intervenții chirurgicale
        surgicalInterventions: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              name: { bsonType: "string" },
              date: { bsonType: "date" },
              hospital: { bsonType: "string" },
              notes: { bsonType: "string" }
            }
          }
        },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 3. Medic (Doctor) Collection
```javascript
db.createCollection("medics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        
        // Date profesionale
        specialization: { bsonType: "string" }, // Obstetrics, Ginecology, etc.
        degree: { bsonType: "string" }, // Dr., Conf., Prof.
        license: { bsonType: "string" },
        
        // Locație práč
        clinic: { bsonType: "string" },
        clinicAddress: { bsonType: "string" },
        city: { bsonType: "string" },
        
        // Disponibilitate (implicită)
        workingHours: {
          bsonType: "object",
          properties: {
            startTime: { bsonType: "string" }, // "09:00"
            endTime: { bsonType: "string" },   // "17:00"
            durationPerSlot: { bsonType: "int" } // minutes, default 30
          }
        },
        
        // Zile libere și excepții
        offDays: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              date: { bsonType: "date" },
              reason: { bsonType: "string" },
              type: { enum: ["vacation", "holiday", "conference", "other"] }
            }
          }
        },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 4. Doctor-Patient Association
```javascript
db.createCollection("doctor_patient_associations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["medicId", "gravidaId", "status", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        medicId: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        status: { enum: ["pending", "accepted", "rejected", "terminated"] },
        
        // Data când a fost inițiată asocierea
        requestedAt: { bsonType: "date" },
        respondedAt: { bsonType: "date" },
        
        // Pentru revocare
        terminatedAt: { bsonType: "date" },
        terminationReason: { bsonType: "string" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 5. Measurements Collection
```javascript
db.createCollection("measurements", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["gravidaId", "type", "value", "date", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Tipuri de măsurători
        type: { enum: ["weight", "bloodPressure", "bloodGlucose"] },
        
        // Date măsurării
        value: { bsonType: "object" }, // pentru bloodPressure: {systolic, diastolic}
        unit: { bsonType: "string" }, // kg, mmHg, mg/dL
        
        // Context
        notes: { bsonType: "string" },
        date: { bsonType: "date" },
        
        // Pentru alert
        isAbnormal: { bsonType: "bool" },
        abnormalReason: { bsonType: "string" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 6. Symptoms Collection
```javascript
db.createCollection("symptoms", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["gravidaId", "symptom", "date", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Tip simptom
        symptom: { 
          enum: ["nausea", "edema", "pain", "sleep", "mood", "fetalMovements", 
                  "bleeding", "discharge", "headache", "dizziness", "other"] 
        },
        
        // Intensitate
        intensity: { enum: ["mild", "moderate", "severe"] },
        
        // Observații
        notes: { bsonType: "string" },
        date: { bsonType: "date" },
        
        // Pentru timeline medicului
        sharedWithDoctor: { bsonType: "bool" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 7. Appointments Collection
```javascript
db.createCollection("appointments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["medicId", "gravidaId", "startTime", "status", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        medicId: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Datetime
        startTime: { bsonType: "date" },
        endTime: { bsonType: "date" },
        duration: { bsonType: "int" }, // minutes
        
        // Status programare
        status: { enum: ["pending", "confirmed", "rejected", "cancelled", "completed"] },
        
        // Note
        reasonForVisit: { bsonType: "string" },
        doctorNotes: { bsonType: "string" }, // Only doctor can modify
        patientNotes: { bsonType: "string" },
        
        // Atașamente
        attachments: { bsonType: "array" }, // IDs de documenten
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 8. Pregnancy Calendar Tasks
```javascript
db.createCollection("pregnancy_calendar_tasks", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["gravidaId", "title", "week", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Task info
        title: { bsonType: "string" },
        description: { bsonType: "string" },
        
        // Planificare pe săptămână
        week: { bsonType: "int" },
        dueDate: { bsonType: "date" },
        
        // Status
        completed: { bsonType: "bool" },
        completedAt: { bsonType: "date" },
        
        // Atașamente (rezultate analize/ecografii)
        attachments: { bsonType: "array" },
        
        // Recomandation source
        recommendedByDoctor: { bsonType: "bool" },
        medicId: { bsonType: "objectId" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 9. Medications Collection
```javascript
db.createCollection("medications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["gravidaId", "medicament", "type", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Medicament info
        medicament: { bsonType: "string" },
        doza: { bsonType: "string" },
        frecventa: { bsonType: "string" }, // "2 ori pe zi", etc
        caieForma: { bsonType: "string" }, // tablets, liquid, injection
        
        // Tipuri
        type: { enum: ["prescribed", "supplement", "otc"] },
        
        // Dacă e prescris
        prescribedByDoctorId: { bsonType: "objectId" },
        indication: { bsonType: "string" },
        
        // Date
        startDate: { bsonType: "date" },
        endDate: { bsonType: "date" },
        instructions: { bsonType: "string" },
        warnings: { bsonType: "string" },
        
        // Aderență
        adherence: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              date: { bsonType: "date" },
              taken: { bsonType: "bool" },
              time: { bsonType: "string" }
            }
          }
        },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 10. Documents Collection
```javascript
db.createCollection("documents", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "filename", "type", "uploadDate", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        medicId: { bsonType: "objectId" }, // if uploaded by doctor
        
        // File info
        filename: { bsonType: "string" },
        fileSize: { bsonType: "int" },
        mimeType: { bsonType: "string" },
        filePath: { bsonType: "string" },
        
        // Metadata
        documentType: { enum: ["labAnalysis", "ultrasound", "prescription", "report", "other"] },
        uploadDate: { bsonType: "date" },
        laboratory: { bsonType: "string" }, // optional
        clinic: { bsonType: "string" }, // optional
        
        // Asociere la programare
        appointmentId: { bsonType: "objectId" },
        
        // Vizibilitate
        visibleToPatient: { bsonType: "bool" },
        visibleToDoctor: { bsonType: "bool" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 11. Messages Collection
```javascript
db.createCollection("messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["senderId", "recipientId", "text", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        senderId: { bsonType: "objectId" },
        recipientId: { bsonType: "objectId" },
        conversationId: { bsonType: "objectId" },
        
        // Message content
        text: { bsonType: "string" },
        
        // Atașamente
        attachments: {
          bsonType: "array",
          items: { bsonType: "objectId" } // Document IDs
        },
        
        // Status
        status: { enum: ["sent", "delivered", "read"] },
        readAt: { bsonType: "date" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 12. Conversations Collection
```javascript
db.createCollection("conversations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["participantIds", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        participantIds: {
          bsonType: "array",
          items: { bsonType: "objectId" },
          minItems: 2,
          maxItems: 2
        },
        
        // Metadata
        lastMessageAt: { bsonType: "date" },
        lastMessage: { bsonType: "string" },
        
        // Persoane
        gravidaId: { bsonType: "objectId" },
        medicId: { bsonType: "objectId" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 13. Recommendations Collection
```javascript
db.createCollection("recommendations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["medicId", "gravidaId", "content", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        medicId: { bsonType: "objectId" },
        gravidaId: { bsonType: "objectId" },
        
        // Recomandare
        title: { bsonType: "string" },
        content: { bsonType: "string" },
        category: { enum: ["nutrition", "exercise", "medication", "monitoring", "testing", "lifestyle", "other"] },
        
        // Status
        isVisible: { bsonType: "bool" },
        isInternal: { bsonType: "bool" }, // Only for doctor's notes
        
        // Date
        dueDate: { bsonType: "date" },
        
        // Atașamente
        attachments: { bsonType: "array" },
        
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

## 14. Pregnancy Weekly Info Collection
```javascript
db.createCollection("pregnancy_weekly_info", {
  properties: {
    _id: { bsonType: "objectId" },
    week: { bsonType: "int" }, // 1-42
    
    // Informații despre mamă
    motherInfo: {
      bsonType: "object",
      properties: {
        symptoms: { bsonType: "array" },
        bodyChanges: { bsonType: "array" },
        emotionalAspects: { bsonType: "array" },
        tipsAndAdvice: { bsonType: "array" }
      }
    },
    
    // Informații despre făt
    fetusInfo: {
      bsonType: "object",
      properties: {
        size: { bsonType: "string" }, // e.g., "size of a grain of rice"
        weight: { bsonType: "string" }, // grams
        developments: { bsonType: "array" },
        images: { bsonType: "array" }
      }
    },
    
    createdAt: { bsonType: "date" }
  }
})
```

## Indexes (Performance)
```javascript
// Users
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ role: 1 })

// Gravidas
db.gravidas.createIndex({ userId: 1 }, { unique: true })

// Measurements
db.measurements.createIndex({ gravidaId: 1, date: -1 })
db.measurements.createIndex({ gravidaId: 1, type: 1 })

// Appointments
db.appointments.createIndex({ medicId: 1, startTime: 1 })
db.appointments.createIndex({ gravidaId: 1 })
db.appointments.createIndex({ status: 1 })

// Messages
db.messages.createIndex({ conversationId: 1, createdAt: -1 })
db.messages.createIndex({ senderId: 1 })
db.messages.createIndex({ recipientId: 1 })

// Documents
db.documents.createIndex({ gravidaId: 1 })
db.documents.createIndex({ medicId: 1 })

// Doctor-Patient Association
db.doctor_patient_associations.createIndex({ medicId: 1, gravidaId: 1 }, { unique: true })
db.doctor_patient_associations.createIndex({ medicId: 1 })
db.doctor_patient_associations.createIndex({ gravidaId: 1 })
```
