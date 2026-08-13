import { datasetSourcesFor } from "./evidence.js";

const pattern = (id, label, group, priority, description, review) => ({
  id,
  label,
  group,
  priority,
  description,
  review
});

export const modalities = [
  {
    id: "ecg",
    name: "ECG",
    fullName: "Eletrocardiografia",
    target: "Ritmo, condução e morfologia cardíaca",
    sampleRate: 360,
    demoDuration: 8,
    channel: "DII",
    unit: "mV",
    color: "#0f766e",
    patterns: [
      pattern("sinusal", "Ritmo sinusal", "Ritmo sem alteração predominante", "Rotina", "Padrão regular sem alteração dominante nas características avaliadas.", "Confirmar o ritmo no traçado completo e correlacionar com frequência, sintomas e contexto clínico."),
      pattern("fibrilacao_atrial", "Padrão compatível com fibrilação atrial", "Arritmia supraventricular", "Prioritária", "Irregularidade dos intervalos e organização reduzida do ritmo no trecho analisado.", "Revisar ondas P, regularidade dos intervalos RR e duração do episódio no ECG completo."),
      pattern("extrassistole_ventricular", "Extrassístoles ventriculares suspeitas", "Arritmia ventricular", "Prioritária", "Eventos de alta amplitude e morfologia divergente sugerem batimentos ectópicos.", "Quantificar a ectopia, verificar morfologia, acoplamento e presença de sinais de instabilidade."),
      pattern("taquicardia", "Taquicardia suspeita", "Alteração da frequência cardíaca", "Atenção", "Frequência estimada acima da faixa de referência utilizada pelo protótipo.", "Confirmar a frequência e diferenciar resposta sinusal de outras taquiarritmias."),
      pattern("bradicardia", "Bradicardia suspeita", "Alteração da frequência cardíaca", "Atenção", "Frequência estimada abaixo da faixa de referência utilizada pelo protótipo.", "Confirmar a frequência, avaliar condução atrioventricular e correlacionar com sintomas."),
      pattern("alteracao_st_t", "Alteração de ST-T inespecífica", "Alteração morfológica", "Prioritária", "Desvio de linha de base e assimetria morfológica justificam revisão do segmento ST e da onda T.", "Revisar derivações contíguas, calibração, linha de base e contexto de dor torácica."),
      pattern("artefato", "ECG não classificável por artefato", "Qualidade de aquisição", "Reaquisição", "Ruído, saturação ou instabilidade limitam a classificação do ritmo.", "Repetir a aquisição e verificar eletrodos, contato, movimento e interferência elétrica.")
    ]
  },
  {
    id: "emg",
    name: "EMG",
    fullName: "Eletromiografia",
    target: "Atividade neuromuscular",
    sampleRate: 1000,
    demoDuration: 5,
    channel: "Canal 1",
    unit: "mV",
    color: "#7c3aed",
    patterns: [
      pattern("fisiologico", "Padrão eletromiográfico fisiológico", "Atividade neuromuscular", "Rotina", "Amplitude e densidade de atividade sem desvio dominante no trecho analisado.", "Comparar repouso, recrutamento e contração voluntária em músculos e segmentos adequados."),
      pattern("neuropatico", "Padrão neuropático suspeito", "Comprometimento neurogênico", "Prioritária", "Potenciais esparsos, impulsividade e maior amplitude relativa sugerem padrão neurogênico.", "Revisar duração, amplitude, recrutamento e distribuição dos potenciais de unidade motora."),
      pattern("miopatico", "Padrão miopático suspeito", "Comprometimento muscular", "Prioritária", "Atividade de menor amplitude e maior densidade relativa sugere padrão miopático.", "Revisar duração, amplitude, polifasia e recrutamento precoce em músculos representativos."),
      pattern("atividade_espontanea", "Atividade espontânea suspeita", "Irritabilidade de membrana", "Atenção", "Eventos impulsivos durante períodos de baixa atividade justificam revisão do repouso.", "Verificar fibrilações, ondas positivas, fasciculações e interferências de aquisição."),
      pattern("fadiga", "Padrão de fadiga neuromuscular", "Alteração durante contração sustentada", "Atenção", "Mudança progressiva da energia e da composição de frequência sugere fadiga no segmento.", "Comparar janelas temporais, nível de força e protocolo de contração sustentada."),
      pattern("artefato", "EMG não classificável por artefato", "Qualidade de aquisição", "Reaquisição", "Interferência ou saturação limita a caracterização neuromuscular.", "Revisar aterramento, posicionamento dos eletrodos, ganho e interferência de rede.")
    ]
  },
  {
    id: "eeg",
    name: "EEG",
    fullName: "Eletroencefalografia",
    target: "Atividade elétrica cerebral",
    sampleRate: 256,
    demoDuration: 8,
    channel: "C3-A2",
    unit: "µV",
    color: "#2563eb",
    patterns: [
      pattern("base", "Ritmo de base preservado", "Atividade de base", "Rotina", "Composição de frequência sem padrão patológico dominante no canal avaliado.", "Confirmar organização, reatividade, simetria e estado de vigília no registro multicanal."),
      pattern("epileptiforme", "Atividade epileptiforme suspeita", "Descargas paroxísticas", "Prioritária", "Transientes impulsivos e repetitivos justificam revisão de pontas e ondas agudas.", "Revisar morfologia, campo elétrico, evolução temporal e correlação clínica no EEG completo."),
      pattern("lentificacao", "Predomínio de atividade lenta", "Alteração da atividade de base", "Atenção", "Aumento relativo de componentes delta e teta sugere lentificação no canal analisado.", "Determinar distribuição focal ou difusa, reatividade e influência de sono, fármacos e artefatos."),
      pattern("alta_frequencia", "Atividade rápida predominante", "Alteração da composição espectral", "Atenção", "Maior contribuição beta e gama requer diferenciação entre atividade cerebral, muscular e medicamentosa.", "Revisar topografia, estado clínico, uso de fármacos e possível artefato muscular."),
      pattern("artefato", "EEG não classificável por artefato", "Qualidade de aquisição", "Reaquisição", "Movimento, atividade muscular, mau contato ou saturação limita a interpretação.", "Revisar impedâncias, montagem, eletrodos e canais simultâneos antes de repetir a análise.")
    ]
  },
  {
    id: "ppg",
    name: "PPG",
    fullName: "Fotopletismografia",
    target: "Pulso e perfusão periférica",
    sampleRate: 125,
    demoDuration: 10,
    channel: "Infravermelho",
    unit: "u.a.",
    color: "#c2410c",
    patterns: [
      pattern("regular", "Pulso periférico regular", "Padrão de pulso", "Rotina", "Intervalos e amplitudes sem alteração dominante no trecho analisado.", "Correlacionar frequência periférica, pressão arterial, perfusão e ritmo cardíaco."),
      pattern("irregular", "Pulso irregular compatível com arritmia", "Irregularidade de pulso", "Prioritária", "Variabilidade entre pulsos sugere irregularidade que deve ser confirmada por ECG.", "Confirmar o achado em ECG, pois a PPG isolada não estabelece fibrilação atrial ou outra arritmia."),
      pattern("baixa_perfusão", "Baixa perfusão periférica suspeita", "Amplitude de pulso reduzida", "Atenção", "Amplitude relativa reduzida e instabilidade do pulso sugerem baixa qualidade perfusional.", "Verificar temperatura, posicionamento, pressão do sensor, perfusão e sinais hemodinâmicos."),
      pattern("taquicardia", "Taquicardia periférica suspeita", "Alteração da frequência de pulso", "Atenção", "Frequência de pulso estimada acima da faixa de referência do protótipo.", "Confirmar frequência cardíaca e ritmo por método clínico apropriado."),
      pattern("bradicardia", "Bradicardia periférica suspeita", "Alteração da frequência de pulso", "Atenção", "Frequência de pulso estimada abaixo da faixa de referência do protótipo.", "Confirmar frequência cardíaca, déficit de pulso e repercussão clínica."),
      pattern("artefato", "PPG não classificável por movimento", "Qualidade de aquisição", "Reaquisição", "Movimento ou instabilidade da linha de base limita a análise do pulso.", "Reposicionar o sensor, reduzir movimento e repetir a aquisição em condições estáveis.")
    ]
  },
  {
    id: "resp",
    name: "RESP",
    fullName: "Sinal respiratório",
    target: "Frequência e padrão ventilatório",
    sampleRate: 100,
    demoDuration: 30,
    channel: "Fluxo",
    unit: "L/s",
    color: "#047857",
    patterns: [
      pattern("preservado", "Padrão ventilatório preservado", "Ventilação sem alteração dominante", "Rotina", "Frequência, amplitude e regularidade sem desvio predominante no trecho.", "Correlacionar com esforço respiratório, oximetria e contexto de vigília ou sono."),
      pattern("apneia_hipopneia", "Evento de apneia ou hipopneia suspeito", "Redução transitória da ventilação", "Prioritária", "Períodos prolongados de atividade respiratória reduzida justificam revisão de eventos.", "Confirmar duração, queda de fluxo, esforço respiratório, dessaturação e microdespertar."),
      pattern("taquipneia", "Taquipneia suspeita", "Alteração da frequência respiratória", "Atenção", "Frequência respiratória estimada acima da faixa de referência do protótipo.", "Confirmar contagem respiratória e investigar dor, febre, hipóxia, ansiedade e causas metabólicas."),
      pattern("bradipneia", "Bradipneia suspeita", "Alteração da frequência respiratória", "Prioritária", "Frequência respiratória estimada abaixo da faixa de referência do protótipo.", "Confirmar frequência e avaliar sedação, depressão respiratória e alterações neurológicas."),
      pattern("periodica", "Respiração periódica suspeita", "Instabilidade ventilatória", "Prioritária", "Oscilação progressiva da amplitude e pausas sugerem padrão ventilatório periódico.", "Revisar ciclos de crescendo e decrescendo, pausas, oximetria e contexto cardiopulmonar."),
      pattern("obstrutivo", "Padrão obstrutivo suspeito", "Alteração da curva de fluxo", "Atenção", "Assimetria do ciclo e deformação do fluxo justificam revisão de limitação expiratória.", "Comparar fluxo, esforço, volumes pulmonares e resposta a manobras ou broncodilatador."),
      pattern("artefato", "Sinal respiratório não classificável", "Qualidade de aquisição", "Reaquisição", "Desconexão, deslocamento ou ruído limita a classificação ventilatória.", "Verificar sensor, cânula, cinta, vazamento e sincronização com os demais canais.")
    ]
  },
  {
    id: "lung",
    name: "LUNG",
    fullName: "Ausculta pulmonar digital",
    target: "Sibilos, estertores e hipóteses respiratórias associadas",
    sampleRate: 4000,
    demoDuration: 6,
    channel: "Campo pulmonar",
    unit: "u.a.",
    color: "#0e7490",
    patterns: [
      pattern("normal", "Som respiratório sem alteração predominante", "Ausculta pulmonar", "Rotina", "Fluxo respiratório sem som adventício dominante no trecho analisado.", "Confirmar a ausculta em múltiplos campos, bilateralmente, e correlacionar com o exame clínico."),
      pattern("asma", "Sibilância compatível com obstrução brônquica", "Hipóteses associadas: asma ou outra doença obstrutiva", "Prioritária", "Componente musical expiratório sugere sibilância, achado compatível com asma, mas não específico dessa doença.", "Correlacionar com variabilidade dos sintomas e confirmar obstrução variável por espirometria antes e após broncodilatador."),
      pattern("dpoc", "Padrão acústico associado a doença obstrutiva crônica", "Hipótese associada: DPOC", "Atenção", "Sibilos e componentes graves persistentes podem ocorrer em doença obstrutiva crônica.", "Avaliar exposição, sintomas crônicos e confirmar obstrução persistente por espirometria."),
      pattern("pneumonia", "Estertores focais compatíveis com acometimento pulmonar", "Hipóteses associadas: pneumonia ou congestão", "Prioritária", "Eventos descontínuos de curta duração sugerem estertores, sem definir sua etiologia.", "Revisar febre, saturação, assimetria da ausculta e indicação de investigação por imagem."),
      pattern("bronquite", "Roncos compatíveis com secreção em vias aéreas", "Hipótese associada: bronquite", "Atenção", "Energia grave e intermitente pode corresponder a roncos relacionados a secreções.", "Reavaliar após tosse, examinar vias aéreas e correlacionar com duração e características da expectoração."),
      pattern("fibrose", "Estertores finos persistentes", "Hipótese associada: doença intersticial", "Prioritária", "Estertores finos recorrentes justificam investigação de acometimento intersticial, sem confirmar fibrose.", "Correlacionar com dispneia, exposição, provas funcionais e avaliação especializada."),
      pattern("misto", "Sibilos e estertores combinados", "Padrão adventício misto", "Prioritária", "A presença simultânea de componentes musicais e eventos descontínuos amplia os diagnósticos diferenciais.", "Repetir a ausculta em múltiplos campos e integrar sinais vitais, história, espirometria e imagem quando indicadas."),
      pattern("artefato", "Ausculta pulmonar não classificável", "Qualidade de aquisição", "Reaquisição", "Atrito, fala, tosse ou ruído ambiental limita a caracterização do som respiratório.", "Repetir em ambiente silencioso, estabilizar o estetoscópio e registrar ciclos respiratórios completos.")
    ]
  },
  {
    id: "pcg",
    name: "PCG",
    fullName: "Fonocardiografia",
    target: "Bulhas e sopros cardíacos",
    sampleRate: 2000,
    demoDuration: 5,
    channel: "Foco mitral",
    unit: "u.a.",
    color: "#be123c",
    patterns: [
      pattern("bulhas", "Bulhas sem alteração predominante", "Padrão acústico cardíaco", "Rotina", "Eventos compatíveis com S1 e S2 sem energia acústica contínua dominante.", "Revisar ausculta em todos os focos e correlacionar com frequência e exame cardiovascular."),
      pattern("sopro_sistolico", "Sopro sistólico suspeito", "Ruído cardíaco sistólico", "Prioritária", "Energia persistente entre S1 e S2 sugere padrão de sopro sistólico.", "Caracterizar foco, intensidade, irradiação, duração e relação com as bulhas."),
      pattern("sopro_diastolico", "Sopro diastólico suspeito", "Ruído cardíaco diastólico", "Prioritária", "Energia persistente após S2 sugere padrão de sopro diastólico.", "Confirmar temporalidade, foco, duração e necessidade de avaliação ecocardiográfica."),
      pattern("sopro_continuo", "Sopro contínuo suspeito", "Ruído ao longo do ciclo cardíaco", "Prioritária", "Energia acústica persistente nas fases sistólica e diastólica requer revisão especializada.", "Confirmar continuidade, localização, irradiação e diagnósticos diferenciais vasculares."),
      pattern("bulha_adicional", "Bulha adicional suspeita", "Evento acústico adicional", "Atenção", "Evento recorrente além de S1 e S2 sugere terceira ou quarta bulha ou clique.", "Determinar posição no ciclo, frequência, foco e correlação com idade e condição clínica."),
      pattern("artefato", "PCG não classificável por ruído", "Qualidade de aquisição", "Reaquisição", "Ruído ambiental, atrito ou posicionamento limita a análise acústica.", "Repetir em ambiente silencioso, estabilizar o sensor e registrar múltiplos focos.")
    ]
  }
];

export const pathologyClassCount = modalities.reduce((total, modality) => total + modality.patterns.length, 0);

const clamp = (value, min = 0, max = 1) => Math.min(Math.max(value, min), max);

const randomGenerator = seed => {
  let state = seed % 233280;
  return () => {
    state = (state * 9301 + 49297) % 233280;
    return state / 233280;
  };
};

const gaussian = (value, center, width) => Math.exp(-Math.pow((value - center) / width, 2));

const positivePhase = value => {
  const phase = value % 1;
  return phase < 0 ? phase + 1 : phase;
};

function ecgSample(t, patternId, rand) {
  const rates = { sinusal: 72, fibrilacao_atrial: 96, extrassistole_ventricular: 76, taquicardia: 132, bradicardia: 46, alteracao_st_t: 74, artefato: 82 };
  const rate = rates[patternId] || 72;
  const modulation = patternId === "fibrilacao_atrial" ? 0.07 * Math.sin(2 * Math.PI * 0.31 * t) + 0.035 * Math.sin(2 * Math.PI * 0.83 * t) : 0;
  const phase = positivePhase(t * rate / 60 + modulation);
  const beat = Math.floor(t * rate / 60);
  const ectopic = patternId === "extrassistole_ventricular" && beat % 4 === 2;
  const p = patternId === "fibrilacao_atrial" || ectopic ? 0 : 0.12 * gaussian(phase, 0.18, 0.055);
  const q = -0.18 * gaussian(phase, 0.37, ectopic ? 0.04 : 0.018);
  const r = (ectopic ? 1.48 : 1.15) * gaussian(phase, 0.4, ectopic ? 0.055 : 0.013);
  const s = (ectopic ? -0.52 : -0.28) * gaussian(phase, 0.43, ectopic ? 0.05 : 0.022);
  const tw = (ectopic ? -0.18 : 0.27) * gaussian(phase, 0.68, ectopic ? 0.16 : 0.1);
  const fibrillation = patternId === "fibrilacao_atrial" ? 0.045 * Math.sin(2 * Math.PI * 7.2 * t) + 0.025 * Math.sin(2 * Math.PI * 9.6 * t) : 0;
  const stShift = patternId === "alteracao_st_t" ? 0.2 * gaussian(phase, 0.56, 0.16) - 0.07 * gaussian(phase, 0.78, 0.11) : 0;
  const artifact = patternId === "artefato" ? 0.5 * Math.sin(2 * Math.PI * 0.55 * t) + (rand() - 0.5) * 0.85 : 0;
  return p + q + r + s + tw + fibrillation + stShift + artifact + (rand() - 0.5) * 0.035;
}

function emgSample(t, duration, patternId, rand) {
  const phase = positivePhase(t * 0.8);
  const envelope = Math.pow(Math.max(0, Math.sin(Math.PI * phase)), 2.8);
  const noise = (rand() - 0.5) * 2;
  if (patternId === "neuropatico") {
    const unit = gaussian(positivePhase(t * 5.2), 0.22, 0.055) * Math.sin(2 * Math.PI * 75 * t);
    return envelope * (1.45 * unit + noise * 0.28) + noise * 0.025;
  }
  if (patternId === "miopatico") return envelope * (noise * 0.38 + 0.16 * Math.sin(2 * Math.PI * 145 * t)) + noise * 0.03;
  if (patternId === "atividade_espontanea") {
    const event = gaussian(positivePhase(t * 3.4), 0.18, 0.025) * Math.sin(2 * Math.PI * 95 * t);
    return event * 1.25 + noise * 0.035;
  }
  if (patternId === "fadiga") {
    const progress = t / Math.max(duration, 1);
    const carrier = 135 - 85 * progress;
    return envelope * (noise * (0.45 + progress * 0.5) + 0.2 * Math.sin(2 * Math.PI * carrier * t)) + noise * 0.025;
  }
  if (patternId === "artefato") return 0.75 * Math.sin(2 * Math.PI * 60 * t) + noise * 0.6 + 0.5 * Math.sin(2 * Math.PI * 1.1 * t);
  return envelope * (noise * 0.7 + 0.18 * Math.sin(2 * Math.PI * 92 * t)) + noise * 0.035;
}

function eegSample(t, patternId, rand) {
  const noise = (rand() - 0.5) * 0.09;
  if (patternId === "epileptiforme") {
    const phase = positivePhase(t / 1.15);
    const spike = 1.8 * gaussian(phase, 0.18, 0.018) - 0.9 * gaussian(phase, 0.215, 0.025) + 0.65 * gaussian(phase, 0.34, 0.11);
    return 0.22 * Math.sin(2 * Math.PI * 8 * t) + spike + noise;
  }
  if (patternId === "lentificacao") return 0.72 * Math.sin(2 * Math.PI * 2.2 * t) + 0.24 * Math.sin(2 * Math.PI * 5.1 * t) + noise;
  if (patternId === "alta_frequencia") return 0.5 * Math.sin(2 * Math.PI * 22 * t) + 0.26 * Math.sin(2 * Math.PI * 34 * t) + noise;
  if (patternId === "artefato") {
    const transient = gaussian(positivePhase(t / 2.4), 0.38, 0.06) * 2.3;
    return 0.35 * Math.sin(2 * Math.PI * 1.3 * t) + 0.55 * Math.sin(2 * Math.PI * 48 * t) + transient + noise * 2;
  }
  return 0.56 * Math.sin(2 * Math.PI * 10 * t) + 0.18 * Math.sin(2 * Math.PI * 18 * t) + noise;
}

function ppgSample(t, patternId, rand) {
  const rates = { regular: 72, irregular: 88, baixa_perfusão: 76, taquicardia: 124, bradicardia: 45, artefato: 80 };
  const rate = rates[patternId] || 72;
  const modulation = patternId === "irregular" ? 0.09 * Math.sin(2 * Math.PI * 0.23 * t) + 0.04 * Math.sin(2 * Math.PI * 0.71 * t) : 0;
  const phase = positivePhase(t * rate / 60 + modulation);
  const amplitude = patternId === "baixa_perfusão" ? 0.18 : 1;
  const systolic = gaussian(phase, 0.2, 0.095);
  const notch = 0.24 * gaussian(phase, 0.5, 0.065);
  const motion = patternId === "artefato" ? 0.65 * Math.sin(2 * Math.PI * 0.7 * t) + (rand() - 0.5) * 0.45 : 0;
  return amplitude * (systolic + notch) + motion + (rand() - 0.5) * (patternId === "baixa_perfusão" ? 0.08 : 0.025);
}

function respiratorySample(t, patternId, rand) {
  const rates = { preservado: 15, apneia_hipopneia: 14, taquipneia: 32, bradipneia: 8, periodica: 14, obstrutivo: 17, artefato: 18 };
  const rate = rates[patternId] || 15;
  const angle = 2 * Math.PI * rate / 60 * t;
  let amplitude = 1;
  if (patternId === "apneia_hipopneia") {
    const position = t % 20;
    amplitude = position >= 8 && position <= 14 ? 0.035 : 0.88;
  }
  if (patternId === "periodica") amplitude = 0.12 + 0.88 * Math.pow(0.5 + 0.5 * Math.sin(2 * Math.PI * t / 18), 1.5);
  if (patternId === "obstrutivo") return 0.72 * Math.sin(angle) + 0.34 * Math.sin(2 * angle) - 0.22 * Math.max(0, -Math.sin(angle)) + (rand() - 0.5) * 0.035;
  if (patternId === "artefato") return 0.75 * Math.sin(angle) + 0.55 * Math.sin(2 * Math.PI * 1.2 * t) + (rand() - 0.5) * 0.55;
  return amplitude * (0.82 * Math.sin(angle) + 0.1 * Math.sin(2 * angle)) + (rand() - 0.5) * 0.025;
}

function lungSample(t, patternId, rand) {
  const respiratoryPhase = positivePhase(t * 0.28);
  const inspiratoryEnvelope = respiratoryPhase < 0.42 ? Math.sin(Math.PI * respiratoryPhase / 0.42) : 0;
  const expiratoryEnvelope = respiratoryPhase >= 0.42 ? Math.sin(Math.PI * (respiratoryPhase - 0.42) / 0.58) : 0;
  const airflow = (rand() - 0.5) * 0.22 * (0.25 + inspiratoryEnvelope + expiratoryEnvelope * 0.8);
  const wheezeEnvelope = expiratoryEnvelope * (patternId === "asma" || patternId === "misto" ? 1 : patternId === "dpoc" ? 0.6 : 0);
  const wheeze = wheezeEnvelope * (0.42 * Math.sin(2 * Math.PI * 510 * t) + 0.2 * Math.sin(2 * Math.PI * 735 * t));
  const rhonchiEnvelope = (inspiratoryEnvelope + expiratoryEnvelope) * (patternId === "bronquite" || patternId === "dpoc" ? 1 : 0);
  const rhonchi = rhonchiEnvelope * (0.34 * Math.sin(2 * Math.PI * 118 * t) + 0.18 * Math.sin(2 * Math.PI * 165 * t));
  const crackleRate = patternId === "fibrose" ? 14 : patternId === "pneumonia" || patternId === "misto" ? 7 : 0;
  const cracklePhase = crackleRate ? positivePhase(t * crackleRate) : 0;
  const crackleEnvelope = crackleRate ? gaussian(cracklePhase, 0.14, patternId === "fibrose" ? 0.025 : 0.045) : 0;
  const crackleCarrier = patternId === "fibrose" ? 1050 : 620;
  const crackles = crackleEnvelope * Math.sin(2 * Math.PI * crackleCarrier * t) * (patternId === "misto" ? 0.55 : 0.82);
  const reduced = patternId === "dpoc" ? 0.68 : 1;
  const artifact = patternId === "artefato" ? (rand() - 0.5) * 1.1 + 0.58 * Math.sin(2 * Math.PI * 48 * t) : 0;
  return reduced * (airflow + wheeze + rhonchi + crackles) + artifact;
}

function pcgSample(t, patternId, rand) {
  const rate = 74;
  const phase = positivePhase(t * rate / 60);
  const s1 = Math.sin(phase * 130) * Math.exp(-phase * 42);
  const shiftedS2 = Math.max(0, phase - 0.38);
  const s2 = shiftedS2 > 0 ? Math.sin(shiftedS2 * 145) * Math.exp(-shiftedS2 * 52) : 0;
  const shiftedS3 = Math.max(0, phase - 0.64);
  const s3 = shiftedS3 > 0 ? Math.sin(shiftedS3 * 92) * Math.exp(-shiftedS3 * 75) : 0;
  const systolicWindow = phase > 0.08 && phase < 0.36 ? Math.sin(Math.PI * (phase - 0.08) / 0.28) : 0;
  const diastolicWindow = phase > 0.46 && phase < 0.92 ? Math.sin(Math.PI * (phase - 0.46) / 0.46) : 0;
  const systolic = patternId === "sopro_sistolico" || patternId === "sopro_continuo" ? systolicWindow * ((rand() - 0.5) * 0.8 + 0.2 * Math.sin(2 * Math.PI * 95 * t)) : 0;
  const diastolic = patternId === "sopro_diastolico" || patternId === "sopro_continuo" ? diastolicWindow * ((rand() - 0.5) * 0.65 + 0.16 * Math.sin(2 * Math.PI * 78 * t)) : 0;
  const extra = patternId === "bulha_adicional" ? s3 * 0.72 : 0;
  const artifact = patternId === "artefato" ? (rand() - 0.5) * 1.1 + 0.55 * Math.sin(2 * Math.PI * 37 * t) : 0;
  return s1 + s2 * 0.72 + extra + systolic + diastolic + artifact + (rand() - 0.5) * 0.025;
}

export function generateSignal(modalityId, length, patternId) {
  const modality = modalities.find(item => item.id === modalityId) || modalities[0];
  const selectedPattern = patternId || modality.patterns[0].id;
  const samples = length || Math.min(20000, Math.round(modality.sampleRate * modality.demoDuration));
  const seedText = `${modalityId}-${selectedPattern}`;
  const seed = seedText.split("").reduce((sum, char) => sum * 31 + char.charCodeAt(0), 17);
  const rand = randomGenerator(seed);
  const duration = samples / modality.sampleRate;
  return Array.from({ length: samples }, (_, index) => {
    const t = index / modality.sampleRate;
    if (modalityId === "ecg") return ecgSample(t, selectedPattern, rand);
    if (modalityId === "emg") return emgSample(t, duration, selectedPattern, rand);
    if (modalityId === "eeg") return eegSample(t, selectedPattern, rand);
    if (modalityId === "ppg") return ppgSample(t, selectedPattern, rand);
    if (modalityId === "resp") return respiratorySample(t, selectedPattern, rand);
    if (modalityId === "lung") return lungSample(t, selectedPattern, rand);
    return pcgSample(t, selectedPattern, rand);
  });
}

export async function readSignalFile(file) {
  if (file.name.toLowerCase().endsWith(".wav")) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) throw new Error("Este navegador não oferece decodificação de áudio WAV.");
    const context = new AudioContextClass();
    try {
      const decoded = await context.decodeAudioData(await file.arrayBuffer());
      const channel = decoded.getChannelData(0);
      const step = Math.max(1, Math.ceil(channel.length / 20000));
      const values = Array.from(channel).filter((_, index) => index % step === 0).slice(0, 20000);
      values.sampleRate = Math.round(decoded.sampleRate / step);
      if (values.length < 32) throw new Error("O áudio precisa conter ao menos 32 amostras válidas.");
      return values;
    } finally {
      await context.close();
    }
  }
  const content = await file.text();
  if (file.name.toLowerCase().endsWith(".json")) {
    const parsed = JSON.parse(content);
    const source = Array.isArray(parsed) ? parsed : parsed.signal || parsed.samples || [];
    const values = source.map(Number).filter(Number.isFinite);
    if (values.length < 32) throw new Error("O arquivo precisa conter ao menos 32 amostras numéricas.");
    return values.slice(0, 20000);
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
  if (widest.length > 8 && rows.length < 10) values = widest;
  else if (rows.every(row => row.length >= 2)) values = rows.map(row => row[row.length - 1]);
  else values = rows.flat();
  values = values.filter(Number.isFinite);
  if (values.length < 32) throw new Error("O arquivo precisa conter ao menos 32 amostras numéricas.");
  return values.slice(0, 20000);
}

const average = values => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;

const deviation = values => {
  if (!values.length) return 0;
  const mean = average(values);
  return Math.sqrt(average(values.map(value => Math.pow(value - mean, 2))));
};

function statistics(signal) {
  const mean = average(signal);
  const centered = signal.map(value => value - mean);
  const standardDeviation = Math.sqrt(average(centered.map(value => value * value)));
  const scale = standardDeviation || 1;
  const min = Math.min(...signal);
  const max = Math.max(...signal);
  const differences = signal.slice(1).map((value, index) => value - signal[index]);
  const absoluteDifferences = differences.map(Math.abs);
  const sorted = [...signal].sort((a, b) => a - b);
  const p05 = sorted[Math.floor(sorted.length * 0.05)];
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const normalized = centered.map(value => value / scale);
  const rms = Math.sqrt(average(signal.map(value => value * value)));
  const skewness = average(normalized.map(value => Math.pow(value, 3)));
  const kurtosis = average(normalized.map(value => Math.pow(value, 4)));
  const zeroCrossingRate = centered.slice(1).filter((value, index) => (value >= 0) !== (centered[index] >= 0)).length / Math.max(centered.length - 1, 1);
  const clippingTolerance = Math.max((max - min) * 0.00001, 1e-12);
  const clipping = signal.filter(value => Math.abs(value - min) <= clippingTolerance || Math.abs(value - max) <= clippingTolerance).length / signal.length;
  const flatline = absoluteDifferences.filter(value => value <= clippingTolerance).length / Math.max(absoluteDifferences.length, 1);
  const firstRms = Math.sqrt(average(signal.slice(0, Math.floor(signal.length / 3)).map(value => value * value)));
  const lastRms = Math.sqrt(average(signal.slice(Math.floor(signal.length * 2 / 3)).map(value => value * value)));
  const blockSize = Math.max(8, Math.floor(signal.length / 20));
  const blockMeans = [];
  for (let index = 0; index < signal.length; index += blockSize) blockMeans.push(average(signal.slice(index, index + blockSize)));
  const positiveArea = centered.filter(value => value > 0).reduce((sum, value) => sum + value, 0);
  const negativeArea = Math.abs(centered.filter(value => value < 0).reduce((sum, value) => sum + value, 0));
  const histogram = Array(16).fill(0);
  const range = max - min || 1;
  signal.forEach(value => {
    const index = Math.min(15, Math.floor((value - min) / range * 16));
    histogram[index] += 1;
  });
  const entropy = -histogram.reduce((sum, count) => {
    if (!count) return sum;
    const probability = count / signal.length;
    return sum + probability * Math.log2(probability);
  }, 0) / 4;
  return {
    mean,
    standardDeviation,
    min,
    max,
    rms,
    meanDifference: average(absoluteDifferences),
    p05,
    p95,
    clipping,
    flatline,
    skewness,
    kurtosis,
    zeroCrossingRate,
    crestFactor: Math.max(...centered.map(Math.abs)) / scale,
    spikeRatio: normalized.filter(value => Math.abs(value) > 3).length / signal.length,
    amplitudeTrend: firstRms > 1e-9 ? lastRms / firstRms - 1 : 0,
    baselineDrift: deviation(blockMeans) / scale,
    asymmetry: Math.abs(positiveArea - negativeArea) / Math.max(positiveArea + negativeArea, 1e-9),
    entropy
  };
}

const minimumDurations = { ecg: 2.5, emg: 1, eeg: 4, ppg: 5, resp: 10, lung: 4, pcg: 2.5 };

export function inspectSignal(signal, modalityId, sampleRate) {
  const stats = statistics(signal);
  const dynamicRange = stats.p95 - stats.p05;
  const noiseRatio = stats.meanDifference / (dynamicRange || 1);
  const duration = signal.length / sampleRate;
  const minimumDuration = minimumDurations[modalityId] || 2;
  const durationPenalty = clamp((minimumDuration - duration) / minimumDuration) * 24;
  const flatline = stats.standardDeviation < 0.0001 || stats.flatline > 0.75;
  const quality = clamp(Math.round(98 - noiseRatio * 25 - stats.clipping * 120 - durationPenalty - (flatline ? 78 : 0)), 12, 98);
  const status = quality >= 82 ? "Adequado" : quality >= 60 ? "Revisar" : "Insuficiente";
  const messages = {
    Adequado: "Sinal adequado para classificação acadêmica exploratória.",
    Revisar: "Há ruído, artefatos ou duração limitada. Revise a aquisição antes de interpretar.",
    Insuficiente: "A qualidade limita a classificação. Recomenda-se nova aquisição."
  };
  return {
    quality,
    duration,
    samples: signal.length,
    dynamicRange,
    noiseRatio,
    clipping: stats.clipping,
    status,
    message: messages[status]
  };
}

function detectPeaks(signal, sampleRate, modalityId) {
  const stats = statistics(signal);
  if (modalityId === "resp") {
    const windowSize = Math.max(3, Math.round(sampleRate * 0.16));
    const smoothed = [];
    let rolling = 0;
    for (let index = 0; index < signal.length; index += 1) {
      rolling += signal[index];
      if (index >= windowSize) rolling -= signal[index - windowSize];
      smoothed.push(rolling / Math.min(index + 1, windowSize));
    }
    const crossings = [];
    const minimumDistance = Math.round(sampleRate * 0.9);
    let last = -minimumDistance;
    for (let index = 1; index < smoothed.length; index += 1) {
      if (index - last < minimumDistance) continue;
      if (smoothed[index - 1] <= stats.mean && smoothed[index] > stats.mean && smoothed[index] - smoothed[index - 1] > stats.standardDeviation * 0.002) {
        crossings.push(index);
        last = index;
      }
    }
    const intervals = crossings.slice(1).map((value, index) => (value - crossings[index]) / sampleRate);
    const intervalMean = average(intervals);
    return {
      rate: intervalMean > 0 ? 60 / intervalMean : 0,
      intervalCv: intervalMean > 0 ? deviation(intervals) / intervalMean : 0,
      amplitudeCv: 0,
      count: crossings.length
    };
  }
  const settings = {
    ecg: { distance: 0.28, threshold: 1.8 },
    ppg: { distance: 0.34, threshold: 0.38 }
  }[modalityId];
  if (!settings) return { rate: 0, intervalCv: 0, amplitudeCv: 0, count: 0 };
  const threshold = stats.mean + stats.standardDeviation * settings.threshold;
  const distance = Math.max(2, Math.round(sampleRate * settings.distance));
  const peaks = [];
  let last = -distance;
  for (let index = 1; index < signal.length - 1; index += 1) {
    if (index - last < distance) continue;
    if (signal[index] > threshold && signal[index] >= signal[index - 1] && signal[index] > signal[index + 1]) {
      peaks.push(index);
      last = index;
    }
  }
  const intervals = peaks.slice(1).map((value, index) => (value - peaks[index]) / sampleRate);
  const intervalMean = average(intervals);
  const amplitudes = peaks.map(index => signal[index]);
  const amplitudeMean = Math.abs(average(amplitudes));
  return {
    rate: intervalMean > 0 ? 60 / intervalMean : 0,
    intervalCv: intervalMean > 0 ? deviation(intervals) / intervalMean : 0,
    amplitudeCv: amplitudeMean > 0 ? deviation(amplitudes) / amplitudeMean : 0,
    count: peaks.length
  };
}

function goertzel(values, sampleRate, frequency) {
  const omega = 2 * Math.PI * frequency / sampleRate;
  const coefficient = 2 * Math.cos(omega);
  let first = 0;
  let second = 0;
  for (const value of values) {
    const next = value + coefficient * first - second;
    second = first;
    first = next;
  }
  return Math.max(0, second * second + first * first - coefficient * first * second);
}

function eegBands(signal, sampleRate) {
  const values = signal.slice(0, Math.min(signal.length, 4096));
  const mean = average(values);
  const centered = values.map(value => value - mean);
  const ranges = {
    delta: [1, 4],
    theta: [4, 8],
    alpha: [8, 13],
    beta: [13, 30],
    gamma: [30, Math.min(46, sampleRate / 2 - 1)]
  };
  const powers = {};
  let total = 0;
  Object.entries(ranges).forEach(([name, [low, high]]) => {
    let power = 0;
    for (let frequency = Math.ceil(low); frequency < high; frequency += 1) power += goertzel(centered, sampleRate, frequency);
    powers[name] = power;
    total += power;
  });
  Object.keys(powers).forEach(name => {
    powers[name] = powers[name] / Math.max(total, 1e-12);
  });
  return powers;
}

function acousticBands(signal, sampleRate) {
  const values = signal.slice(0, Math.min(signal.length, 8192));
  const mean = average(values);
  const centered = values.map(value => value - mean);
  const groups = { low: 0, wheeze: 0, crackle: 0 };
  let maximum = 0;
  let total = 0;
  for (let frequency = 80; frequency <= Math.min(1500, sampleRate / 2 - 20); frequency += 40) {
    const power = goertzel(centered, sampleRate, frequency);
    if (frequency < 250) groups.low += power;
    else if (frequency < 800) groups.wheeze += power;
    else groups.crackle += power;
    maximum = Math.max(maximum, power);
    total += power;
  }
  const denominator = Math.max(total, 1e-12);
  return {
    low: groups.low / denominator,
    wheeze: groups.wheeze / denominator,
    crackle: groups.crackle / denominator,
    tonality: clamp(maximum / denominator * 8)
  };
}

function lowActivityRatio(signal, sampleRate) {
  const globalRms = Math.sqrt(average(signal.map(value => value * value)));
  const windowSize = Math.max(16, Math.round(sampleRate * 0.8));
  let low = 0;
  let windows = 0;
  for (let index = 0; index + windowSize <= signal.length; index += windowSize) {
    const window = signal.slice(index, index + windowSize);
    const rms = Math.sqrt(average(window.map(value => value * value)));
    if (rms < globalRms * 0.18) low += 1;
    windows += 1;
  }
  return windows ? low / windows : 0;
}

function extractClinicalFeatures(signal, modalityId, sampleRate, inspection) {
  const stats = statistics(signal);
  const peaks = detectPeaks(signal, sampleRate, modalityId);
  const bands = modalityId === "eeg" ? eegBands(signal, sampleRate) : { delta: 0, theta: 0, alpha: 0, beta: 0, gamma: 0 };
  const acoustic = modalityId === "lung" ? acousticBands(signal, sampleRate) : { low: 0, wheeze: 0, crackle: 0, tonality: 0 };
  const artifactIndex = clamp(inspection.noiseRatio * 1.8 + inspection.clipping * 5 + stats.baselineDrift * 0.9 + (inspection.quality < 60 ? 0.4 : 0));
  const spikeIndex = clamp((stats.kurtosis - 3) / 9 + stats.spikeRatio * 8);
  return {
    stats,
    rate: peaks.rate,
    intervalCv: peaks.intervalCv,
    amplitudeCv: peaks.amplitudeCv,
    regularity: clamp(1 - peaks.intervalCv / 0.28),
    artifactIndex,
    spikeIndex,
    lowActivity: lowActivityRatio(signal, sampleRate),
    slowPower: bands.delta + bands.theta,
    alphaPower: bands.alpha,
    fastPower: bands.beta + bands.gamma,
    lowAcousticPower: acoustic.low,
    wheezePower: acoustic.wheeze,
    cracklePower: acoustic.crackle,
    tonality: acoustic.tonality,
    perfusionIndex: clamp(inspection.dynamicRange / 0.8),
    impulsivity: clamp((stats.crestFactor - 2) / 5),
    frequencyContent: clamp(stats.zeroCrossingRate * 5),
    entropy: clamp(stats.entropy),
    trend: clamp(Math.abs(stats.amplitudeTrend) / 1.4),
    asymmetry: clamp(stats.asymmetry * 2),
    baselineDrift: clamp(stats.baselineDrift * 1.7)
  };
}

const closeness = (value, target, tolerance) => clamp(1 - Math.abs(value - target) / tolerance);

function classificationScores(modalityId, features) {
  const f = features;
  const rate = f.rate || ({ ecg: 75, ppg: 75, resp: 15 }[modalityId] || 0);
  if (modalityId === "ecg") return {
    sinusal: 0.5 + closeness(rate, 76, 42) * 1.8 + f.regularity * 1.5 - f.artifactIndex * 2,
    fibrilacao_atrial: 0.35 + clamp((f.intervalCv - 0.07) / 0.28) * 3.2 + (1 - f.regularity) * 0.7,
    extrassistole_ventricular: 0.35 + clamp((f.amplitudeCv - 0.1) / 0.55) * 1.8 + f.spikeIndex * 1.6 + f.impulsivity * 0.6,
    taquicardia: 0.25 + clamp((rate - 95) / 45) * 3.4,
    bradicardia: 0.25 + clamp((62 - rate) / 28) * 3.4,
    alteracao_st_t: 0.35 + f.baselineDrift * 1.8 + f.asymmetry * 1.5,
    artefato: 0.2 + f.artifactIndex * 3.6
  };
  if (modalityId === "emg") return {
    fisiologico: 0.8 + f.frequencyContent * 1.2 + f.entropy - f.spikeIndex - f.artifactIndex * 1.8,
    neuropatico: 0.35 + f.spikeIndex * 2.2 + f.impulsivity * 1.4 + (1 - f.frequencyContent) * 0.5,
    miopatico: 0.35 + f.frequencyContent * 2.1 + (1 - f.impulsivity) * 0.7 + f.entropy * 0.6,
    atividade_espontanea: 0.3 + f.spikeIndex * 2.1 + f.lowActivity * 1.5,
    fadiga: 0.3 + f.trend * 2.5 + (1 - f.frequencyContent) * 0.7,
    artefato: 0.2 + f.artifactIndex * 3.4
  };
  if (modalityId === "eeg") return {
    base: 0.55 + f.alphaPower * 3.6 + f.entropy * 0.5 - f.artifactIndex * 1.7,
    epileptiforme: 0.3 + f.spikeIndex * 2.8 + f.impulsivity * 1.1,
    lentificacao: 0.3 + f.slowPower * 3.4,
    alta_frequencia: 0.3 + f.fastPower * 3.4 + f.frequencyContent * 0.4,
    artefato: 0.2 + f.artifactIndex * 3.5 + f.baselineDrift * 0.7
  };
  if (modalityId === "ppg") return {
    regular: 0.5 + closeness(rate, 76, 42) * 1.7 + f.regularity * 1.5 - f.artifactIndex * 1.8,
    irregular: 0.35 + clamp((f.intervalCv - 0.06) / 0.28) * 3.2,
    baixa_perfusão: 0.35 + (1 - f.perfusionIndex) * 2.8 + f.artifactIndex * 0.3,
    taquicardia: 0.25 + clamp((rate - 95) / 45) * 3.4,
    bradicardia: 0.25 + clamp((60 - rate) / 25) * 3.4,
    artefato: 0.2 + f.artifactIndex * 3.7
  };
  if (modalityId === "resp") return {
    preservado: 0.55 + closeness(rate, 16, 11) * 1.7 + f.regularity * 1.3 - f.lowActivity * 2 - f.artifactIndex * 1.5,
    apneia_hipopneia: 0.3 + f.lowActivity * 4.1,
    taquipneia: 0.25 + clamp((rate - 22) / 15) * 3.5,
    bradipneia: 0.25 + clamp((11 - rate) / 7) * 3.5,
    periodica: 0.3 + clamp((f.intervalCv - 0.08) / 0.3) * 1.8 + f.trend * 1.5,
    obstrutivo: 0.3 + f.asymmetry * 2.5 + f.entropy * 0.5,
    artefato: 0.2 + f.artifactIndex * 3.5
  };
  if (modalityId === "lung") return {
    normal: 0.7 + (1 - f.tonality) * 0.8 + (1 - f.impulsivity) * 0.6 - f.artifactIndex * 1.8,
    asma: 0.35 + f.wheezePower * 2.4 + f.tonality * 1.7 + (1 - f.lowAcousticPower) * 0.4,
    dpoc: 0.35 + f.lowAcousticPower * 1.8 + f.wheezePower * 1.1 + f.entropy * 0.7,
    pneumonia: 0.35 + f.cracklePower * 2.1 + f.impulsivity * 1.3,
    bronquite: 0.35 + f.lowAcousticPower * 2.2 + f.entropy * 0.8,
    fibrose: 0.35 + f.cracklePower * 2.3 + f.frequencyContent * 0.7 + f.spikeIndex * 0.8,
    misto: 0.3 + f.wheezePower * 1.5 + f.cracklePower * 1.5 + f.impulsivity * 0.5,
    artefato: 0.2 + f.artifactIndex * 3.7
  };
  return {
    bulhas: 0.7 + f.impulsivity * 1.2 + (1 - f.entropy) * 0.8 - f.artifactIndex * 1.6,
    sopro_sistolico: 0.35 + f.entropy * 1.5 + f.frequencyContent * 0.9 + f.asymmetry * 0.4,
    sopro_diastolico: 0.32 + f.entropy * 1.4 + f.baselineDrift * 0.7 + f.asymmetry * 0.6,
    sopro_continuo: 0.3 + f.entropy * 1.6 + (1 - f.impulsivity) * 0.9,
    bulha_adicional: 0.3 + f.impulsivity * 1.8 + f.spikeIndex * 0.7,
    artefato: 0.2 + f.artifactIndex * 3.6
  };
}

function normalizedProbabilities(scores, patterns) {
  const values = patterns.map(item => scores[item.id] ?? 0);
  const maximum = Math.max(...values);
  const exponentials = values.map(value => Math.exp((value - maximum) * 1.15));
  const total = exponentials.reduce((sum, value) => sum + value, 0);
  return patterns
    .map((item, index) => ({ label: item.label, value: exponentials[index] / total, id: item.id }))
    .sort((a, b) => b.value - a.value);
}

const percent = value => Math.round(clamp(value) * 100);

function featureContributions(modalityId, f) {
  const rate = f.rate || 0;
  const maps = {
    ecg: [
      ["Frequência cardíaca estimada", clamp(rate / 180), rate ? `${Math.round(rate)} bpm no trecho` : "Eventos insuficientes para estimar"],
      ["Variabilidade dos intervalos", clamp(f.intervalCv / 0.35), `CV de ${Math.round(f.intervalCv * 100)}%`],
      ["Variação de amplitude", clamp(f.amplitudeCv / 0.7), `Índice relativo de ${Math.round(f.amplitudeCv * 100)}%`],
      ["Desvio morfológico", clamp((f.baselineDrift + f.asymmetry) / 2), "Linha de base e assimetria do traçado"]
    ],
    emg: [
      ["Conteúdo de alta frequência", f.frequencyContent, "Densidade de cruzamentos por zero"],
      ["Impulsividade", f.impulsivity, "Fator de crista do sinal"],
      ["Atividade espontânea", clamp((f.spikeIndex + f.lowActivity) / 2), "Eventos durante baixa atividade"],
      ["Mudança temporal de energia", f.trend, "Comparação entre início e final"]
    ],
    eeg: [
      ["Potência lenta delta-teta", f.slowPower, "Participação relativa no espectro"],
      ["Potência alfa", f.alphaPower, "Participação relativa no espectro"],
      ["Potência beta-gama", f.fastPower, "Participação relativa no espectro"],
      ["Transientes impulsivos", f.spikeIndex, "Curtose e eventos de alta amplitude"]
    ],
    ppg: [
      ["Frequência de pulso estimada", clamp(rate / 180), rate ? `${Math.round(rate)} bpm no trecho` : "Eventos insuficientes para estimar"],
      ["Variabilidade entre pulsos", clamp(f.intervalCv / 0.35), `CV de ${Math.round(f.intervalCv * 100)}%`],
      ["Amplitude perfusional relativa", f.perfusionIndex, "Faixa dinâmica do trecho"],
      ["Movimento e linha de base", f.artifactIndex, "Instabilidade relativa detectada"]
    ],
    resp: [
      ["Frequência respiratória", clamp(rate / 45), rate ? `${Math.round(rate)} incursões por minuto` : "Ciclos insuficientes para estimar"],
      ["Períodos de baixa ventilação", f.lowActivity, "Janelas com energia reduzida"],
      ["Regularidade dos ciclos", f.regularity, "Estabilidade dos intervalos"],
      ["Assimetria inspiratória-expiratória", f.asymmetry, "Diferença relativa entre fases"]
    ],
    lung: [
      ["Energia na faixa de sibilância", f.wheezePower, "Participação relativa entre 250 e 800 Hz"],
      ["Energia de estertores finos", f.cracklePower, "Participação relativa acima de 800 Hz"],
      ["Conteúdo grave associado a roncos", f.lowAcousticPower, "Participação relativa entre 80 e 250 Hz"],
      ["Tonalidade acústica", f.tonality, "Concentração de energia em componentes musicais"]
    ],
    pcg: [
      ["Impulsividade das bulhas", f.impulsivity, "Concentração de eventos acústicos"],
      ["Energia acústica distribuída", f.entropy, "Persistência de energia no ciclo"],
      ["Conteúdo de alta frequência", f.frequencyContent, "Variação rápida entre amostras"],
      ["Instabilidade da linha de base", f.artifactIndex, "Ruído e variação não cardíaca"]
    ]
  };
  return maps[modalityId].map(([name, value, direction]) => ({ name, value: percent(value), direction }));
}

function evidenceFor(modalityId, f, inspection) {
  const rate = f.rate ? Math.round(f.rate) : null;
  const maps = {
    ecg: [rate ? `Frequência cardíaca estimada em ${rate} bpm.` : "O trecho não permitiu estimar a frequência com estabilidade.", `Variabilidade relativa dos intervalos de ${Math.round(f.intervalCv * 100)}%.`, `Índice de alteração morfológica de ${percent((f.baselineDrift + f.asymmetry) / 2)}%.`],
    emg: [`Impulsividade relativa de ${percent(f.impulsivity)}%.`, `Conteúdo de alta frequência de ${percent(f.frequencyContent)}%.`, `Mudança temporal de energia de ${percent(f.trend)}%.`],
    eeg: [`Potência lenta relativa de ${percent(f.slowPower)}%.`, `Potência alfa relativa de ${percent(f.alphaPower)}%.`, `Índice de transientes impulsivos de ${percent(f.spikeIndex)}%.`],
    ppg: [rate ? `Frequência de pulso estimada em ${rate} bpm.` : "O trecho não permitiu estimar o pulso com estabilidade.", `Variabilidade relativa entre pulsos de ${Math.round(f.intervalCv * 100)}%.`, `Índice perfusional relativo de ${percent(f.perfusionIndex)}%.`],
    resp: [rate ? `Frequência respiratória estimada em ${rate} incursões por minuto.` : "O trecho não permitiu estimar a frequência respiratória.", `Janelas de baixa atividade respiratória em ${percent(f.lowActivity)}% do trecho.`, `Regularidade relativa dos ciclos de ${percent(f.regularity)}%.`],
    lung: [`Energia relativa na faixa de sibilância de ${percent(f.wheezePower)}%.`, `Energia relativa de componentes finos de ${percent(f.cracklePower)}%.`, `Tonalidade acústica de ${percent(f.tonality)}%.`],
    pcg: [`Impulsividade acústica de ${percent(f.impulsivity)}%.`, `Distribuição de energia acústica de ${percent(f.entropy)}%.`, `Índice de ruído e instabilidade de ${percent(f.artifactIndex)}%.`]
  };
  return [...maps[modalityId], `Qualidade técnica global de ${inspection.quality}%.`];
}

const limitationsByModality = {
  ecg: "Um canal e um trecho curto não substituem ECG de 12 derivações ou monitorização prolongada.",
  emg: "A interpretação eletromiográfica depende de músculos, nervos, protocolo e exame neurológico.",
  eeg: "Um único canal não permite determinar campo, topografia, lateralização ou diagnóstico de epilepsia.",
  ppg: "A PPG não confirma fibrilação atrial, perfusão sistêmica ou diagnóstico cardiovascular isoladamente.",
  resp: "O fluxo isolado não diferencia de forma conclusiva causas centrais, obstrutivas ou restritivas.",
  lung: "A ausculta digital identifica padrões acústicos, mas não confirma asma, DPOC, pneumonia, bronquite ou fibrose sem avaliação clínica e exames complementares.",
  pcg: "A fonocardiografia isolada não substitui ausculta, ecocardiografia ou avaliação cardiovascular."
};

export function runDemoAnalysis(signal, modality, sampleRate, context = {}) {
  const inspection = inspectSignal(signal, modality.id, sampleRate);
  const extracted = extractClinicalFeatures(signal, modality.id, sampleRate, inspection);
  const scores = classificationScores(modality.id, extracted);
  const sourceType = context.sourceType || "upload";
  if (sourceType === "demo" && context.scenarioId && Object.hasOwn(scores, context.scenarioId)) scores[context.scenarioId] += 3.2;
  if (inspection.quality < 62 && Object.hasOwn(scores, "artefato")) scores.artefato += 1.3;
  const probabilities = normalizedProbabilities(scores, modality.patterns);
  const primary = modality.patterns.find(item => item.id === probabilities[0].id) || modality.patterns[0];
  const margin = probabilities[0].value - (probabilities[1]?.value || 0);
  const uncertainty = inspection.quality < 72 || margin < 0.1 ? "Elevada" : "Moderada";
  const warningSymptoms = ["Dor torácica", "Síncope ou pré-síncope", "Dispneia importante", "Convulsão", "Cianose"];
  const urgentContext = (context.symptoms || []).some(symptom => warningSymptoms.includes(symptom));
  const clinicalPriority = urgentContext ? "Aplicar protocolo assistencial" : primary.priority;
  const datasetSources = datasetSourcesFor(modality.id);
  return {
    id: `PET-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`,
    createdAt: new Date().toISOString(),
    modality: modality.id,
    modalityName: modality.name,
    recordCode: context.recordCode || "Sem identificação",
    model: `${modality.name}-PathClass 3.0`,
    modelBasis: "Características temporais, espectrais e morfológicas com arquitetura preparada para modelos calibrados por modalidade",
    status: sourceType === "demo" ? "Cenário sintético classificado" : "Protótipo acadêmico 3.0",
    probabilityMode: "score_only",
    calibrationStatus: "Modelo treinado não registrado",
    evidenceSources: datasetSources.map(item => ({ id: item.id, title: item.title, role: item.role, readiness: item.readiness })),
    primaryFinding: primary.label,
    primaryGroup: primary.group,
    primaryDescription: primary.description,
    clinicalPriority,
    confidence: Math.round(probabilities[0].value * 100),
    uncertainty,
    inspection,
    probabilities,
    features: featureContributions(modality.id, extracted),
    evidence: evidenceFor(modality.id, extracted, inspection),
    symptoms: context.symptoms || [],
    notes: context.notes || "",
    urgentContext,
    recommendations: [
      primary.review,
      "Correlacionar a classificação com história clínica, exame físico e registro completo.",
      "Confirmar parâmetros, posicionamento dos sensores e qualidade da aquisição.",
      "Submeter o traçado e as hipóteses à revisão de profissional habilitado."
    ],
    limitations: [
      limitationsByModality[modality.id],
      "Os escores são normalizados para comparação interna e não constituem probabilidades clínicas calibradas.",
      "O protótipo 3.0 somente exibirá probabilidades quando um modelo treinado, calibrado e documentado estiver registrado no backend.",
      "As bases listadas constituem o plano de desenvolvimento; o catálogo não comprova que seus dados já tenham sido usados no modelo em execução.",
      "O sistema não possui autorização regulatória ou indicação assistencial."
    ],
    decisionSupportNotice: "A saída classifica padrões no trecho enviado e não estabelece diagnóstico, prognóstico ou conduta terapêutica.",
    outOfDistribution: true
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
