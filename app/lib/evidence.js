export const datasetCatalog = [
  {
    id: "mit-bih-arrhythmia",
    modality: "ecg",
    title: "MIT-BIH Arrhythmia Database",
    institution: "MIT-BIH · PhysioNet",
    scale: "48 registros, 47 participantes e cerca de 110 mil anotações de batimentos",
    labels: "Batimentos e ritmos arrítmicos",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/mitdb/1.0.0/",
    role: "Referência para classificação de batimentos",
    readiness: "Preparada para integração",
    limitation: "Coorte pequena e histórica; exige separação por participante."
  },
  {
    id: "ptb-xl",
    modality: "ecg",
    title: "PTB-XL",
    institution: "PTB · PhysioNet",
    scale: "21.837 ECGs de 12 derivações, 18.885 participantes e 71 afirmações clínicas",
    labels: "Diagnóstico, morfologia e ritmo",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/ptb-xl/1.0.3/",
    role: "Treinamento multirrótulo e avaliação por paciente",
    readiness: "Preparada para integração",
    limitation: "Distribuição clínica e equipamentos específicos da coorte."
  },
  {
    id: "chapman-shaoxing-ningbo",
    modality: "ecg",
    title: "Chapman-Shaoxing-Ningbo ECG",
    institution: "Chapman University e hospitais de Shaoxing e Ningbo · PhysioNet",
    scale: "45.152 ECGs de 12 derivações",
    labels: "Ritmos e condições cardiovasculares anotadas por especialistas",
    access: "Aberto",
    license: "Conforme termo da versão oficial",
    url: "https://physionet.org/content/ecg-arrhythmia/1.0.0/",
    role: "Validação geográfica e ampliação de ritmos",
    readiness: "Preparada para integração",
    limitation: "Mapeamento dos rótulos precisa ser harmonizado com SCP-ECG."
  },
  {
    id: "mit-bih-af",
    modality: "ecg",
    title: "MIT-BIH Atrial Fibrillation Database",
    institution: "MIT-BIH · PhysioNet",
    scale: "25 registros de aproximadamente 10 horas",
    labels: "Fibrilação atrial, flutter, ritmo juncional e outros ritmos",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/afdb/1.0.0/",
    role: "Detecção temporal de fibrilação atrial",
    readiness: "Preparada para integração",
    limitation: "Número reduzido de participantes e registros ambulatoriais históricos."
  },
  {
    id: "physionet-emg",
    modality: "emg",
    title: "Examples of Electromyograms",
    institution: "Beth Israel Deaconess Medical Center · PhysioNet",
    scale: "Três exemplos clínicos",
    labels: "Saudável, neuropatia e miopatia",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/emgdb/1.0.0/",
    role: "Validação técnica do processamento",
    readiness: "Referência limitada",
    limitation: "Um participante por classe; não permite estimar desempenho clínico."
  },
  {
    id: "uci-lower-limb-emg",
    modality: "emg",
    title: "EMG Dataset in Lower Limb",
    institution: "UCI Machine Learning Repository",
    scale: "132 sequências de 22 participantes",
    labels: "Movimentos e presença de anormalidade do joelho",
    access: "Aberto",
    license: "CC BY 4.0",
    url: "https://archive.ics.uci.edu/dataset/278/emg+dataset+in+lower+limb",
    role: "Avaliação de generalização em sEMG",
    readiness: "Requer harmonização",
    limitation: "Não oferece rótulos suficientes para neuropatia ou miopatia."
  },
  {
    id: "chb-mit",
    modality: "eeg",
    title: "CHB-MIT Scalp EEG Database",
    institution: "Children's Hospital Boston e MIT · PhysioNet",
    scale: "664 arquivos de 22 participantes e 198 crises anotadas",
    labels: "Segmentos ictais e não ictais",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/chbmit/1.0.0/",
    role: "Detecção de crises com divisão por participante",
    readiness: "Preparada para integração",
    limitation: "Coorte pediátrica com epilepsia farmacorresistente."
  },
  {
    id: "siena-eeg",
    modality: "eeg",
    title: "Siena Scalp EEG Database",
    institution: "University of Siena · PhysioNet",
    scale: "14 participantes, 47 crises e cerca de 128 horas",
    labels: "Crises classificadas por especialista",
    access: "Aberto",
    license: "Conforme termo da versão oficial",
    url: "https://physionet.org/content/siena-scalp-eeg/1.0.0/",
    role: "Validação externa em adultos",
    readiness: "Preparada para integração",
    limitation: "Pequeno número de participantes."
  },
  {
    id: "mimic-iii-ext-ppg",
    modality: "ppg",
    title: "MIMIC-III-Ext-PPG",
    institution: "PhysioNet",
    scale: "Cerca de 6,3 milhões de segmentos de 6.189 participantes",
    labels: "Ritmo sinusal, fibrilação atrial, flutter, bloqueio e estimulação",
    access: "Credenciado",
    license: "Termos MIMIC e PhysioNet",
    url: "https://physionet.org/content/mimic-iii-ext-ppg/1.1.0/",
    role: "Treinamento de ritmo por PPG em larga escala",
    readiness: "Acesso institucional necessário",
    limitation: "População de terapia intensiva e rótulos próximos, não simultâneos, ao segmento."
  },
  {
    id: "bidmc-ppg-resp",
    modality: "ppg",
    title: "BIDMC PPG and Respiration Dataset",
    institution: "Beth Israel Deaconess Medical Center · PhysioNet",
    scale: "53 registros de oito minutos",
    labels: "PPG, ECG, respiração, SpO₂ e incursões respiratórias",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/bidmc/1.0.0/",
    role: "Validação de frequência e qualidade cardiorrespiratória",
    readiness: "Preparada para integração",
    limitation: "Não contém diagnóstico primário de arritmia para todos os segmentos."
  },
  {
    id: "apnea-ecg",
    modality: "resp",
    title: "Apnea-ECG Database",
    institution: "PhysioNet",
    scale: "70 registros noturnos de aproximadamente sete a dez horas",
    labels: "Anotações por minuto de apneia e respiração normal",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/apnea-ecg/1.0.0/",
    role: "Detecção acadêmica de eventos de apneia",
    readiness: "Preparada para integração",
    limitation: "Os rótulos foram derivados de sinais respiratórios simultâneos, não apenas do ECG."
  },
  {
    id: "bidmc-resp",
    modality: "resp",
    title: "BIDMC PPG and Respiration Dataset",
    institution: "Beth Israel Deaconess Medical Center · PhysioNet",
    scale: "53 registros com incursões anotadas por dois avaliadores",
    labels: "Respiração por impedância e frequência respiratória",
    access: "Aberto",
    license: "ODC Attribution 1.0",
    url: "https://physionet.org/content/bidmc/1.0.0/",
    role: "Controle de qualidade e estimação respiratória",
    readiness: "Preparada para integração",
    limitation: "Não permite diagnosticar asma ou doença restritiva."
  },
  {
    id: "challenge-2016-pcg",
    modality: "pcg",
    title: "PhysioNet/CinC Challenge 2016",
    institution: "PhysioNet e Computing in Cardiology",
    scale: "3.126 registros de cinco bases",
    labels: "Normal, anormal e qualidade do registro",
    access: "Aberto",
    license: "Conforme termo da competição",
    url: "https://physionet.org/content/challenge-2016/1.0.0/",
    role: "Generalização entre dispositivos e ambientes",
    readiness: "Preparada para integração",
    limitation: "Rótulo anormal amplo, sem etiologia uniforme."
  },
  {
    id: "circor-pcg",
    modality: "pcg",
    title: "CirCor DigiScope Phonocardiogram Dataset",
    institution: "DigiScope e PhysioNet",
    scale: "5.282 gravações de 1.568 participantes pediátricos",
    labels: "Presença, localização e características de sopros",
    access: "Aberto",
    license: "Conforme termo da versão oficial",
    url: "https://physionet.org/content/circor-heart-sound/1.0.3/",
    role: "Detecção e caracterização de sopros",
    readiness: "Preparada para integração",
    limitation: "Predomínio pediátrico."
  },
  {
    id: "icbhi-2017",
    modality: "lung",
    title: "ICBHI 2017 Respiratory Sound Database",
    institution: "ICBHI Challenge",
    scale: "920 gravações, 126 participantes e 6.898 ciclos respiratórios",
    labels: "Normal, sibilos, estertores e combinação",
    access: "Pesquisa",
    license: "Verificação necessária no portal oficial",
    url: "https://bhichallenge.med.auth.gr/ICBHI_2017_Challenge",
    role: "Detecção de sons adventícios",
    readiness: "Requer revisão de licença",
    limitation: "Há apenas um participante com asma em análises publicadas; não sustenta probabilidade específica de asma."
  },
  {
    id: "kauh-lung",
    modality: "lung",
    title: "KAUH Lung Sound Dataset",
    institution: "King Abdullah University Hospital · Mendeley Data",
    scale: "337 gravações de 112 participantes",
    labels: "Asma, DPOC, pneumonia, bronquite, insuficiência cardíaca, fibrose e derrame pleural",
    access: "Aberto",
    license: "CC BY 4.0",
    url: "https://data.mendeley.com/datasets/jwyy9np4gv/3",
    role: "Pesquisa de hipóteses associadas a doenças pulmonares",
    readiness: "Preparada para integração",
    limitation: "Poucos participantes por doença e dependência do dispositivo de aquisição."
  }
];

export const datasetCount = datasetCatalog.length;

export function datasetSourcesFor(modalityId) {
  return datasetCatalog.filter(item => item.modality === modalityId);
}

export function datasetSummaryFor(modalityId) {
  const sources = datasetSourcesFor(modalityId);
  return {
    count: sources.length,
    titles: sources.map(item => item.title),
    accessLimited: sources.some(item => item.access === "Credenciado"),
    ready: sources.filter(item => item.readiness === "Preparada para integração").length
  };
}
