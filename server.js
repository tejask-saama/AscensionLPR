const express = require('express');
const path = require('path');
const http = require('http');
const app = express();
const port = 3009;
const lprApiPort = 5002; // Port for the Archive LPR API

// Middleware to parse JSON
app.use(express.json());

// Enable CORS for all routes
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  next();
});

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, 'dist/ascension-frontend')));

// Serve node_modules for any dependencies
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));

// Function to proxy requests to the LPR API
function proxyToLprApi(req, res, path, method = 'GET', requestBody = null) {
  console.log(`Proxying ${method} request to LPR API: ${path}`);
  
  const options = {
    hostname: 'localhost',
    port: lprApiPort,
    path: path,
    method: method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    let data = '';
    
    proxyRes.on('data', (chunk) => {
      data += chunk;
    });
    
    proxyRes.on('end', () => {
      try {
        // Try to parse the response as JSON
        const jsonData = JSON.parse(data);
        res.status(proxyRes.statusCode).json(jsonData);
      } catch (error) {
        console.error('Error parsing JSON response from LPR API:', error);
        res.status(500).json({ error: 'Error processing response from LPR API' });
      }
    });
  });

  proxyReq.on('error', (error) => {
    console.error('Error proxying request to LPR API:', error);
    res.status(500).json({ error: 'Error connecting to LPR API' });
  });

  if (requestBody && (method === 'POST' || method === 'PUT')) {
    proxyReq.write(JSON.stringify(requestBody));
  }

  proxyReq.end();
}

// Sample patient data
const patients = [
  {
    id: 1,
    name: "Doe, John",
    dob: "03/15/1975",
    age: 49,
    gender: "Male",
    mrn: "P001"
  },
  {
    id: 2,
    name: "Smith, Mary",
    dob: "05/20/1980",
    age: 43,
    gender: "Female",
    mrn: "P002"
  }
];

// Sample patient details
const patientDetails = {
  1: {
    // Section 1: Patient Information
    id: 1,
    name: 'Doe, John',
    dob: '03/15/1975',
    age: 49,
    gender: 'Male',
    mrn: 'P001',
    
    // Section 2: Background
    background: {
      pastMedicalHistory: 'History of coronary artery disease, essential hypertension, type 2 diabetes mellitus, and paroxysmal supraventricular tachycardia. Hospitalized in April 2024 for SVT; successfully treated with Adenosine.',
      currentPlanInfo: 'Presented to ED on 2024-04-10 with chest pain and shortness of breath. ECG showed narrow complex tachycardia consistent with SVT.'
    },
    
    // Section 3: Assessment
    assessment: {
      vitalSigns: {
        bp: '132/78',
        hr: '72',
        temp: '37.0 °C',
        rr: '16',
        o2Saturation: '96%'
      },
      painLevel: '0/10',
      goalPainLevel: '0/10',
      abnormalFindings: 'Elevated BP readings over 140/90, HbA1c consistently > 6.5%, and ECG showing narrow complex tachycardia.',
      recentPRN: 'Adenosine 6 mg IV push, may repeat 12 mg if needed (2024-04-10)',
      fallRisk: 'Low',
      activity: 'As tolerated',
      wounds: 'None',
      specimen: 'None',
      ivs: 'None',
      procedures: 'None',
      diet: 'Regular',
      safety: 'None',
      labResults: 'Total Cholesterol: 185 mg/dL (2024-04-11)\nLDL Cholesterol: 110 mg/dL (2024-04-11)\nBlood Glucose: 142 mg/dL (2024-04-10)\nHbA1c: 6.4% (2024-04-11)'
    },
    
    // Section 4: Recommendations
    recommendations: {
      shiftGoal: 'Stabilize cardiovascular status, manage hypertension and diabetes, monitor for recurrence of SVT.',
      dayPlan: 'Continue home medications including Lisinopril, Metformin, Atorvastatin, and Aspirin. Monitor BP and blood glucose levels.',
      dischargePlan: 'Discharged in stable condition after SVT episode. Follow up with Dr. Rodriguez in 2 weeks.'
    },
    
    // Section 5: Nurses' Notes
    nursesNotes: [
      {
        date: '04/25/2024',
        time: '14:25 CST',
        user: 'Nurse Johnson',
        content: 'Follow-up after hospitalization for SVT. Patient reports feeling well with no recurrence of palpitations. Notes persistent dry cough, likely from Lisinopril. BP well-controlled at 132/78.'
      },
      {
        date: '04/12/2024',
        time: '13:30 CST',
        user: 'Nurse Williams',
        content: 'Patient is being discharged in stable condition after SVT episode that resolved with Adenosine. No recurrence during 48-hour observation. Continue all home medications.'
      },
      {
        date: '04/11/2024',
        time: '09:15 CST',
        user: 'Nurse Garcia',
        content: 'Hospital day 1. Patient remained in NSR overnight. No further episodes of SVT. Patient reports mild dry cough, possibly related to Lisinopril, but wishes to continue medication as benefits outweigh side effects at this time.'
      }
    ]
  },
  2: {
    id: 2,
    name: 'Smith, Mary',
    dob: '05/20/1980',
    age: 43,
    gender: 'Female',
    mrn: 'P002',
    
    // Section 2: Background
    background: {
      pastMedicalHistory: 'History of asthma, allergic rhinitis, and migraine headaches. Hospitalized once in 2023 for severe asthma exacerbation requiring brief ICU stay.',
      currentPlanInfo: 'Recent increase in migraine frequency, possibly related to work stress. Currently on preventive therapy with propranolol and sumatriptan as needed for acute attacks.'
    },
    
    // Section 3: Assessment
    assessment: {
      vitalSigns: {
        bp: '118/72',
        hr: '68',
        temp: '36.8 °C',
        rr: '14',
        o2Saturation: '98%'
      },
      painLevel: '2/10',
      goalPainLevel: '0/10',
      abnormalFindings: 'Occasional wheezing on deep expiration. Reports mild frontal headache (2/10) that started this morning.',
      recentPRN: 'Albuterol inhaler 2 puffs yesterday evening for mild wheezing',
      fallRisk: 'Low',
      activity: 'As tolerated',
      wounds: 'None',
      specimen: 'None',
      ivs: 'None',
      procedures: 'None',
      diet: 'Regular',
      safety: 'None',
      labResults: 'CBC, BMP within normal limits (2024-03-15)\nPeak flow: 380 L/min (80% of personal best)'
    },
    
    // Section 4: Recommendations
    recommendations: {
      shiftGoal: 'Monitor respiratory status and headache symptoms',
      dayPlan: 'Continue current medication regimen. Encourage use of peak flow meter twice daily. Discuss migraine triggers and stress management techniques.',
      dischargePlan: 'Follow up with primary care in 1 month and neurology in 3 months for migraine management.'
    },
    
    // Section 5: Nurses' Notes
    nursesNotes: [
      {
        date: '05/10/2024',
        time: '10:15 CST',
        user: 'Nurse Thompson',
        content: 'Patient presents for follow-up of asthma and migraine management. Reports good control of asthma symptoms with current regimen but notes increased frequency of migraines (2-3 per week). Vital signs stable. Lungs clear to auscultation.'
      },
      {
        date: '03/15/2024',
        time: '14:45 CST',
        user: 'Nurse Davis',
        content: 'Routine check-up. Patient reports overall good control of asthma with occasional use of rescue inhaler (1-2 times per week). Migraine frequency stable at approximately 1 per month. Discussed importance of avoiding triggers and maintaining regular sleep schedule.'
      }
    ]
  }
};

// API endpoint to get all patients
app.get('/api/patients', (req, res) => {
  // Proxy to Archive API server
  proxyToLprApi(req, res, '/api/lpr-app/patients');
});

// API endpoint to get patient LPR data
app.get('/api/lpr/:patientId', (req, res) => {
  const patientId = parseInt(req.params.patientId);
  const patientDetail = patientDetails[patientId];
  
  if (patientDetail) {
    res.json(patientDetail);
  }
});

// API endpoint for smart assistant questions
app.post('/api/assistant', (req, res) => {
  const { question, patientId } = req.body;
  
  if (!question || !patientId) {
    return res.status(400).json({ error: 'Question and patientId are required' });
  }
  
  // Convert numeric ID to format expected by Archive API (P001, P002, etc.)
  const formattedPatientId = `P${patientId.toString().padStart(3, '0')}`;
  
  // Prepare payload for Archive API
  const payload = {
    patient_id: formattedPatientId,
    query: question
  };
  
  // Proxy to Archive API server
  proxyToLprApi(req, res, '/api/lpr-app/lpr', 'POST', payload);
});

// API endpoint to get patient detail
app.get('/api/patients/:id', (req, res) => {
  const id = parseInt(req.params.id);
  // Convert numeric ID to format expected by Archive API (P001, P002, etc.)
  const patientId = `P${id.toString().padStart(3, '0')}`;
  const query = req.query.query || 'Generate a comprehensive longitudinal patient record';
  
  // Proxy to Archive API server
  proxyToLprApi(req, res, `/api/lpr-app/lpr/${patientId}?query=${encodeURIComponent(query)}`);
});

// Serve the demo.html file at the root URL
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/ascension-frontend/index.html'));
});

// Catch all other routes and return the index file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/ascension-frontend/index.html'));
});

// Real-time LPR API endpoint with dynamic data generation
app.get('/api/realtime/lpr/:patientId', (req, res) => {
  const patientId = parseInt(req.params.patientId);
  
  // First check if the patient exists in our mock data
  const patient = patientDetails[patientId];
  if (!patient) {
    return res.status(404).json({ error: 'Patient not found' });
  }
  
  // Convert numeric ID to format expected by Archive API (P001, P002, etc.)
  const formattedPatientId = `P${patientId.toString().padStart(3, '0')}`;
  
  // Generate mock data since we're not actually connecting to the Archive API in this endpoint
  
  // Simulate database fetch with some dynamic data
  const now = new Date();
  const timestamp = now.toISOString();
  const formattedTime = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
  const formattedDate = now.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
  
  // Generate dynamic vital signs with slight variations
  const baseHR = parseInt(patient.assessment.vitalSigns.hr);
  const baseBP = patient.assessment.vitalSigns.bp.split('/');
  const baseSys = parseInt(baseBP[0]);
  const baseDia = parseInt(baseBP[1]);
  const baseO2 = parseInt(patient.assessment.vitalSigns.o2Saturation.replace(/\D+/g, '')); // remove non-numeric characters
  
  // Add random variations to simulate real-time changes
  const hrVariation = Math.floor(Math.random() * 7) - 3; // -3 to +3
  const sysVariation = Math.floor(Math.random() * 9) - 4; // -4 to +4
  const diaVariation = Math.floor(Math.random() * 7) - 3; // -3 to +3
  const o2Variation = Math.floor(Math.random() * 5) - 2; // -2 to +2
  
  // Create updated vital signs
  const updatedVitalSigns = {
    hr: Math.max(60, Math.min(120, baseHR + hrVariation)),
    bp: `${Math.max(90, Math.min(160, baseSys + sysVariation))}/${Math.max(60, Math.min(100, baseDia + diaVariation))}`,
    o2: Math.max(88, Math.min(100, baseO2 + o2Variation))
  };
  
  // Create a new nurse note
  const newNote = {
    date: formattedDate,
    time: `${formattedTime} CST`,
    user: "System Update",
    content: `Real-time vital signs updated. Patient status monitored.`
  };
  
  // Create a data object with the patient's information and updated vital signs
  const realtimeData = {
    patientId: patientId,
    name: patient.name,
    timestamp: timestamp,
    vitalSigns: updatedVitalSigns,
    alerts: [],
    medicationAdministration: [],
    labResults: [],
    imagingResults: []
  };
  
  // Add some simulated lab results if they don't exist
  if (!realtimeData.labResults) {
    realtimeData.labResults = [
      {
        name: "Complete Blood Count",
        date: formattedDate,
        results: [
          { test: "WBC", value: "6.2", unit: "K/uL", flag: "normal", reference: "4.5-11.0" },
          { test: "RBC", value: "4.8", unit: "M/uL", flag: "normal", reference: "4.5-5.9" },
          { test: "Hgb", value: "14.2", unit: "g/dL", flag: "normal", reference: "13.5-17.5" },
          { test: "Hct", value: "42.1", unit: "%", flag: "normal", reference: "41.0-53.0" },
          { test: "Plt", value: "250", unit: "K/uL", flag: "normal", reference: "150-400" }
        ]
      },
      {
        name: "Basic Metabolic Panel",
        date: formattedDate,
        results: [
          { test: "Sodium", value: "138", unit: "mmol/L", flag: "normal", reference: "136-145" },
          { test: "Potassium", value: "4.0", unit: "mmol/L", flag: "normal", reference: "3.5-5.1" },
          { test: "Chloride", value: "101", unit: "mmol/L", flag: "normal", reference: "98-107" },
          { test: "CO2", value: "24", unit: "mmol/L", flag: "normal", reference: "21-32" },
          { test: "BUN", value: "15", unit: "mg/dL", flag: "normal", reference: "7-20" },
          { test: "Creatinine", value: "0.9", unit: "mg/dL", flag: "normal", reference: "0.6-1.2" },
          { test: "Glucose", value: "110", unit: "mg/dL", flag: "high", reference: "70-99" }
        ]
      }
    ];
  }
  
  // Add medication administration data if it doesn't exist
  if (!realtimeData.medicationAdministration) {
    realtimeData.medicationAdministration = [
      {
        medication: "Lisinopril",
        dose: "10 mg",
        route: "PO",
        time: formattedTime,
        administrator: "Nurse Johnson"
      },
      {
        medication: "Metformin",
        dose: "500 mg",
        route: "PO",
        time: formattedTime,
        administrator: "Nurse Johnson"
      }
    ];
  }
  
  // Add imaging results if they don't exist
  if (!realtimeData.imagingResults) {
    realtimeData.imagingResults = [
      {
        study: "Chest X-ray",
        date: formattedDate,
        findings: "No acute cardiopulmonary process. Heart size normal. Lungs clear.",
        impression: "Normal chest radiograph.",
        radiologist: "Dr. Sarah Williams"
      }
    ];
  }
  
  // Simulate a database query delay (100-300ms)
  setTimeout(() => {
    res.json({
      success: true,
      timestamp: timestamp,
      data: realtimeData
    });
  }, Math.floor(Math.random() * 200) + 100);
});

// Add routes to proxy all Archive API endpoints
app.all('/api/lpr-app/*', (req, res) => {
  const path = req.path;
  proxyToLprApi(req, res, path, req.method, req.body);
});

app.listen(port, () => {
  console.log(`Longitudinal Patient Record running at http://localhost:${port}`);
  console.log(`Archive API proxy available at http://localhost:${port}/api/lpr-app/*`);
  console.log(`Real-time LPR API available at http://localhost:${port}/api/realtime/lpr/:patientId`);
});
