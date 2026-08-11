export const modalities = [
  {
    id: "ecg",
    name: "ECG",
    fullName: "Eletrocardiografia",
    target: "Ritmo e morfologia cardíaca",
    sampleRate: 360,
    channel: "DII",
    unit: "mV",
    color: "#0f766e",
    labels: [
      "Ritmo sinusal",
      "Extrassístole ventricular",
      "Irregularidade compatível com FA",
      "Alteração morfológica inespecífica"
    ]
  },
  {
    id: "emg",
    name: "EMG",
    fullName: "Eletromiografia",
    target: "Atividade neuromuscular",
    sampleRate: 1000,
    channel: "Canal 1",
    unit: "mV",
    color: "#7c3aed",
    labels: [
      "Padrão fisiológico",
      "Padrão neuropático",
      "Padrão miopático",
      "Atividade espontânea"
    ]
  },
  {
    id: "eeg",
    name: "EEG",
    fullName: "Eletroencefalografia",
    target: "Atividade elétrica cerebral",
    sampleRate: 256,
    channel: "C3-A2",
    unit: "µV",
    color: "#2563eb",
    labels: [
      "Ritmo de base esperado",
      "Descarga epileptiforme suspeita",
      "Lentificação focal",
      "Predomínio de artefato"
    ]
  },
  {
    id: "ppg",
    name: "PPG",
    fullName: "Fotopletismografia",
    target: "Pulso e perfusão periférica",
    sampleRate: 125,
    channel: "Infravermelho",
    unit: "u.a.",
    color: "#c2410c",
    labels: [
      "Pulso regular",
      "Irregularidade de pulso",
      "Baixa perfusão",
      "Artefato de movimento"
    ]
  },
  {
    id: "resp",
    name: "RESP",
    fullName: "Sinal respiratório",
    target: "Padrão ventilatório",
    sampleRate: 100,
    channel: "Fluxo",
    unit: "L/s",
    color: "#047857",
    labels: [
      "Padrão ventilatório preservado",
      "Padrão obstrutivo suspeito",
      "Padrão restritivo suspeito",
      "Evento respiratório suspeito"
    ]
  },
  {
    id: "pcg",
    name: "PCG",
    fullName: "Fonocardiografia",
    target: "Bulhas e sopros cardíacos",
    sampleRate: 2000,
    channel: "Foco mitral",
    unit: "u.a.",
    color: "#be123c",
    labels: [
      "Bulhas sem alteração detectável",
      "Sopro sistólico suspeito",
      "Sopro diastólico suspeito",
      "Ruído de aquisição"
    ]
  }
];

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const randomGenerator = seed => {
  let state = seed;
  return () => {
    state = (state * 9301 + 49297) % 233280;
    return state / 233280;
  };
};

export function generateSignal(modalityId, length = 1400) {
  const rand = randomGenerator(modalityId.split("").reduce((sum, char) => sum + char.charCodeAt(0), 17));
  return Array.from({ length }, (_, index) => {
    const t = index / length;
    const noise = (rand() - 0.5) * 0.08;
    if (modalityId === "ecg") {
      const phase = (t * 12) % 1;
      const p = 0.12 * Math.exp(-Math.pow((phase - 0.18) / 0.055, 2));
      const q = -0.18 * Math.exp(-Math.pow((phase - 0.37) / 0.018, 2));
      const r = 1.15 * Math.exp(-Math.pow((phase - 0.4) / 0.013, 2));
      const s = -0.28 * Math.exp(-Math.pow((phase - 0.43) / 0.022, 2));
      const tw = 0.27 * Math.exp(-Math.pow((phase - 0.68) / 0.1, 2));
      return p + q + r + s + tw + noise * 0.45;
    }
    if (modalityId === "emg") {
      const burst = Math.pow(Math.max(0, Math.sin(t * Math.PI * 7)), 3);
      return burst * ((rand() - 0.5) * 1.8 + Math.sin(index * 0.7) * 0.16) + noise;
    }
    if (modalityId === "eeg") {
      return 0.46 * Math.sin(t * Math.PI * 28) + 0.22 * Math.sin(t * Math.PI * 74) + noise * 1.6;
    }
    if (modalityId === "ppg") {
      const phase = (t * 9) % 1;
      const systolic = Math.exp(-Math.pow((phase - 0.22) / 0.1, 2));
      const notch = 0.24 * Math.exp(-Math.pow((phase - 0.52) / 0.07, 2));
      return systolic + notch + noise * 0.35;
    }
    if (modalityId === "resp") {
      return 0.82 * Math.sin(t * Math.PI * 6) + 0.12 * Math.sin(t * Math.PI * 12) + noise * 0.5;
    }
    const phase = (t * 11) % 1;
    const s1 = Math.sin(phase * 90) * Math.exp(-phase * 45);
    const shifted = Math.max(0, phase - 0.38);
    const s2 = Math.sin(shifted * 100) * Math.exp(-shifted * 60);
    return s1 + s2 * 0.7 + noise * 0.3;
  });
}

export async function readSignalFile(file) {
  const content = await file.text();
  if (file.name.toLowerCase().endsWith(".json")) {
    const parsed = JSON.parse(content);
    const source = Array.isArray(parsed) ? parsed : parsed.signal || parsed.samples || [];
    const values = source.map(Number).filter(Number.isFinite);
    if (values.length < 32) throw new Error("O arquivo precisa conter ao menos 32 amostras numéricas.");
    return values;
  }
  const rows = content
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
    .map(line => line.split(/[;,\t ]+/).map(Number).filter(Number.isFinite))
    .filter(row => row.length);
  if (!rows.length) throw new Error("Não foram encontradas amostras numéricas no arquivo.");
  const widest = rows.reduce((best, row) => row.length > best.length ? row : best, []);
  let values;
  if (widest.length > 8 && rows.length < 10) {
    values = widest;
  } else if (rows.every(row => row.length >= 2)) {
    values = rows.map(row => row[row.length - 1]);
  } else {
    values = rows.flat();
  }
  values = values.filter(Number.isFinite);
  if (values.length < 32) throw new Error("O arquivo precisa conter ao menos 32 amostras numéricas.");
  return values.slice(0, 20000);
}

function statistics(signal) {
  const mean = signal.reduce((sum, value) => sum + value, 0) / signal.length;
  const variance = signal.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / signal.length;
  const standardDeviation = Math.sqrt(variance) || 1;
  const min = Math.min(...signal);
  const max = Math.max(...signal);
  const differences = signal.slice(1).map((value, index) => Math.abs(value - signal[index]));
  const meanDifference = differences.reduce((sum, value) => sum + value, 0) / differences.length;
  const sorted = [...signal].sort((a, b) => a - b);
  const p05 = sorted[Math.floor(sorted.length * 0.05)];
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const clipping = signal.filter(value => value === min || value === max).length / signal.length;
  return { mean, standardDeviation, min, max, meanDifference, p05, p95, clipping };
}

export function inspectSignal(signal, modalityId, sampleRate) {
  const stats = statistics(signal);
  const dynamicRange = stats.p95 - stats.p05;
  const noiseRatio = stats.meanDifference / (dynamicRange || 1);
  const flatline = stats.standardDeviation < 0.0001;
  const quality = clamp(Math.round(97 - noiseRatio * 26 - stats.clipping * 110 - (flatline ? 75 : 0)), 18, 98);
  const duration = signal.length / sampleRate;
  return {
    quality,
    duration,
    samples: signal.length,
    dynamicRange,
    noiseRatio,
    clipping: stats.clipping,
    status: quality >= 85 ? "Adequado" : quality >= 65 ? "Revisar" : "Insuficiente",
    message: quality >= 85
      ? "Sinal adequado para análise exploratória."
      : quality >= 65
        ? "Há indícios de ruído ou artefatos. Revise a aquisição."
        : "A qualidade limita a interpretação. Recomenda-se nova aquisição."
  };
}

const focusByModality = { ecg: 0, emg: 0, eeg: 0, ppg: 0, resp: 0, pcg: 0 };

const featureNames = {
  ecg: ["Variabilidade RR", "Morfologia do QRS", "Regularidade do ritmo", "Energia espectral"],
  emg: ["RMS do sinal", "Frequência mediana", "Duração dos potenciais", "Taxa de cruzamento por zero"],
  eeg: ["Potência alfa", "Relação teta/beta", "Entropia espectral", "Assimetria entre canais"],
  ppg: ["Intervalo entre pulsos", "Tempo de subida", "Índice de perfusão", "Variação de amplitude"],
  resp: ["Frequência respiratória", "Regularidade dos ciclos", "Relação inspiração/expiração", "Amplitude ventilatória"],
  pcg: ["Energia sistólica", "Energia diastólica", "Duração S1–S2", "Entropia acústica"]
};

export function runDemoAnalysis(signal, modality, sampleRate, context = {}) {
  const inspection = inspectSignal(signal, modality.id, sampleRate);
  const focus = focusByModality[modality.id];
  const primary = inspection.quality < 55 ? modality.labels.length - 1 : focus;
  const mainProbability = inspection.quality < 55 ? 0.58 : 0.56 + inspection.quality / 500;
  const remaining = (1 - mainProbability) / (modality.labels.length - 1);
  const probabilities = modality.labels
    .map((label, index) => ({ label, value: index === primary ? mainProbability : remaining }))
    .sort((a, b) => b.value - a.value);
  const stats = statistics(signal);
  const featureValues = [
    clamp(38 + stats.meanDifference * 80, 18, 91),
    clamp(32 + stats.standardDeviation * 45, 14, 88),
    clamp(79 - inspection.noiseRatio * 90, 12, 92),
    clamp(44 + inspection.dynamicRange * 24, 20, 90)
  ];
  const features = featureNames[modality.id].map((name, index) => ({
    name,
    value: Math.round(featureValues[index]),
    direction: index % 3 === 0 ? "Aumenta a prioridade" : "Reduz a prioridade"
  }));
  const warningSymptoms = ["Dor torácica", "Síncope ou pré-síncope", "Dispneia importante"];
  const urgentContext = (context.symptoms || []).some(symptom => warningSymptoms.includes(symptom));
  return {
    id: `PET-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`,
    createdAt: new Date().toISOString(),
    modality: modality.id,
    modalityName: modality.name,
    recordCode: context.recordCode || "Sem identificação",
    model: `${modality.name}-demo 0.4`,
    status: "Simulação acadêmica",
    primaryFinding: probabilities[0].label,
    confidence: Math.round(probabilities[0].value * 100),
    uncertainty: inspection.quality >= 80 ? "Moderada" : "Elevada",
    inspection,
    probabilities,
    features,
    symptoms: context.symptoms || [],
    notes: context.notes || "",
    urgentContext,
    recommendations: [
      "Correlacionar o resultado com história clínica, exame físico e traçado completo.",
      "Confirmar a qualidade do posicionamento dos sensores e os parâmetros de aquisição.",
      "Submeter o traçado e as hipóteses à revisão de profissional habilitado."
    ]
  };
}

export function formatDate(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
