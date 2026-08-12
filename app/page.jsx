"use client";

import { useMemo, useRef, useState } from "react";
import {
  downloadJson,
  formatDate,
  generateSignal,
  inspectSignal,
  modalities,
  readSignalFile,
  runDemoAnalysis
} from "./lib/clinical";
import { analyzeWithBackend } from "./lib/api";

const navigation = [
  ["overview", "Visão geral", "01"],
  ["analysis", "Nova análise", "02"],
  ["cases", "Casos analisados", "03"]
];

const symptoms = [
  "Assintomático",
  "Palpitações",
  "Dor torácica",
  "Síncope ou pré-síncope",
  "Dispneia importante",
  "Fraqueza muscular",
  "Tremor",
  "Alteração do sono"
];

function LogoMark() {
  return (
    <div className="logo-mark" aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
    </div>
  );
}

function Waveform({ signal, color = "#0f766e", compact = false }) {
  const points = useMemo(() => {
    if (!signal?.length) return "";
    const width = compact ? 280 : 920;
    const height = compact ? 82 : 220;
    const target = compact ? 160 : 520;
    const step = Math.max(1, Math.floor(signal.length / target));
    const sampled = signal.filter((_, index) => index % step === 0).slice(0, target);
    const min = Math.min(...sampled);
    const max = Math.max(...sampled);
    const range = max - min || 1;
    return sampled.map((value, index) => {
      const x = (index / Math.max(sampled.length - 1, 1)) * width;
      const y = height - ((value - min) / range) * (height * 0.72) - height * 0.14;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
  }, [signal, compact]);
  return (
    <svg className={compact ? "waveform compact" : "waveform"} viewBox={compact ? "0 0 280 82" : "0 0 920 220"} role="img" aria-label="Visualização do sinal fisiológico">
      <defs>
        <pattern id={compact ? "small-grid" : "signal-grid"} width="23" height="22" patternUnits="userSpaceOnUse">
          <path d="M 23 0 L 0 0 0 22" fill="none" stroke="#dfe7e5" strokeWidth="0.7" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill={`url(#${compact ? "small-grid" : "signal-grid"})`} rx="12" />
      <polyline points={points} fill="none" stroke={color} strokeWidth={compact ? "1.8" : "2.4"} strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

function Ring({ value, label, tone = "teal" }) {
  const degrees = Math.round(value * 3.6);
  return (
    <div className={`ring ${tone}`} style={{ background: `conic-gradient(var(--ring-color) ${degrees}deg, #e7eceb ${degrees}deg)` }}>
      <div>
        <strong>{value}%</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}

function EmptyState({ onStart }) {
  return (
    <div className="empty-state">
      <div className="empty-signal"><LogoMark /></div>
      <h3>Nenhuma análise nesta sessão</h3>
      <p>Inicie com uma amostra demonstrativa ou envie um sinal anonimizado.</p>
      <button className="button primary" onClick={onStart}>Iniciar análise</button>
    </div>
  );
}

export default function Home() {
  const [activePage, setActivePage] = useState("overview");
  const [selectedModality, setSelectedModality] = useState(modalities[0]);
  const [signal, setSignal] = useState([]);
  const [fileName, setFileName] = useState("");
  const [sampleRate, setSampleRate] = useState(modalities[0].sampleRate);
  const [recordCode, setRecordCode] = useState("PET-2026-001");
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = JSON.parse(localStorage.getItem("pet-saude-cases") || "[]");
      return Array.isArray(saved) ? saved : [];
    } catch {
      return [];
    }
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const inputRef = useRef(null);

  const quality = useMemo(() => signal.length ? inspectSignal(signal, selectedModality.id, sampleRate) : null, [signal, selectedModality, sampleRate]);

  const chooseModality = modality => {
    setSelectedModality(modality);
    setSampleRate(modality.sampleRate);
    setSignal([]);
    setFileName("");
    setResult(null);
    setError("");
  };

  const loadDemo = modality => {
    chooseModality(modality);
    setSignal(generateSignal(modality.id));
    setFileName(`amostra_${modality.id}_demonstrativa.csv`);
    setActivePage("analysis");
  };

  const handleFile = async file => {
    if (!file) return;
    setError("");
    try {
      const values = await readSignalFile(file);
      setSignal(values);
      setFileName(file.name);
      setResult(null);
    } catch (exception) {
      setError(exception.message || "Não foi possível processar o arquivo.");
    }
  };

  const toggleSymptom = symptom => {
    setSelectedSymptoms(current => current.includes(symptom) ? current.filter(item => item !== symptom) : [...current, symptom]);
  };

  const analyze = async () => {
    if (!signal.length) return;
    setBusy(true);
    setError("");
    try {
      const context = { recordCode, symptoms: selectedSymptoms, notes };
      const response = await analyzeWithBackend({
        modality: selectedModality.id,
        samples: signal,
        sampleRate,
        recordCode,
        symptoms: selectedSymptoms,
        notes
      });
      setResult(response || runDemoAnalysis(signal, selectedModality, sampleRate, context));
    } catch {
      setResult(runDemoAnalysis(signal, selectedModality, sampleRate, { recordCode, symptoms: selectedSymptoms, notes }));
      setError("A API Python não respondeu. A saída exibida corresponde à simulação acadêmica local.");
    } finally {
      setBusy(false);
    }
  };

  const saveCase = () => {
    if (!result) return;
    const saved = [result, ...history.filter(item => item.id !== result.id)].slice(0, 20);
    setHistory(saved);
    localStorage.setItem("pet-saude-cases", JSON.stringify(saved));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("pet-saude-cases");
  };

  const navigate = page => {
    setActivePage(page);
    setMobileMenu(false);
  };

  return (
    <main className="app-shell">
      <aside className={mobileMenu ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <LogoMark />
          <div>
            <strong>PET-Saúde</strong>
            <span>Sinais clínicos</span>
          </div>
        </div>
        <nav aria-label="Navegação principal">
          {navigation.map(([id, label, number]) => (
            <button key={id} className={activePage === id ? "nav-item active" : "nav-item"} onClick={() => navigate(id)}>
              <span>{number}</span>{label}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <strong>Projeto PET-Saúde</strong>
          <p>Análise acadêmica de sinais fisiológicos.</p>
        </div>
        <div className="sidebar-footer">Projeto PET-Saúde · UCPel</div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <button className="menu-button" aria-label="Abrir menu" onClick={() => setMobileMenu(!mobileMenu)}>Menu</button>
          <div>
            <span className="eyebrow">Apoio à leitura de sinais fisiológicos</span>
            <strong>Clínica Escola</strong>
          </div>
          <div className="topbar-project">PET-Saúde · UCPel</div>
        </header>

        <div className="content">
          {activePage === "overview" && (
            <Overview history={history} onStart={() => navigate("analysis")} onDemo={loadDemo} />
          )}
          {activePage === "analysis" && (
            <AnalysisPage
              modality={selectedModality}
              onModality={chooseModality}
              signal={signal}
              fileName={fileName}
              sampleRate={sampleRate}
              onSampleRate={setSampleRate}
              quality={quality}
              inputRef={inputRef}
              onFile={handleFile}
              onDemo={() => loadDemo(selectedModality)}
              recordCode={recordCode}
              onRecordCode={setRecordCode}
              selectedSymptoms={selectedSymptoms}
              onSymptom={toggleSymptom}
              notes={notes}
              onNotes={setNotes}
              result={result}
              busy={busy}
              error={error}
              acknowledged={acknowledged}
              onAcknowledged={setAcknowledged}
              onAnalyze={analyze}
              onSave={saveCase}
            />
          )}
          {activePage === "cases" && (
            <CasesPage history={history} onStart={() => navigate("analysis")} onClear={clearHistory} />
          )}
        </div>
      </section>
    </main>
  );
}

function Overview({ history, onStart, onDemo }) {
  const recent = history.slice(0, 3);
  return (
    <div className="page overview-page">
      <section className="overview-header">
        <div className="hero-copy">
          <span className="section-kicker dark">PET-Saúde</span>
          <h1>Análise de sinais fisiológicos</h1>
          <p>Selecione uma modalidade, envie o arquivo do exame e consulte a avaliação de qualidade e a pré-análise acadêmica.</p>
          <div className="hero-actions">
            <button className="button primary" onClick={onStart}>Nova análise</button>
          </div>
        </div>
      </section>

      <section className="summary-grid">
        <article className="summary-card">
          <span className="summary-label">Modalidades preparadas</span>
          <strong>6</strong>
          <p>ECG, EMG, EEG, PPG, RESP e PCG</p>
        </article>
        <article className="summary-card">
          <span className="summary-label">Casos nesta sessão</span>
          <strong>{history.length}</strong>
          <p>Armazenamento exclusivo no navegador</p>
        </article>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <span className="section-kicker dark">Comece por uma modalidade</span>
            <h2>Análises disponíveis</h2>
          </div>
          <button className="text-button" onClick={onStart}>Ver fluxo completo →</button>
        </div>
        <div className="modality-grid">
          {modalities.map(modality => (
            <button className="modality-card" key={modality.id} onClick={() => onDemo(modality)}>
              <div className="modality-top">
                <span className="modality-code" style={{ color: modality.color, background: `${modality.color}12` }}>{modality.name}</span>
                <span className="arrow">↗</span>
              </div>
              <h3>{modality.fullName}</h3>
              <p>{modality.target}</p>
              <div className="mini-wave"><Waveform signal={generateSignal(modality.id, 420)} color={modality.color} compact /></div>
              <span className="demo-link">Abrir amostra demonstrativa</span>
            </button>
          ))}
        </div>
      </section>

      <section className="section-block recent-section">
        <div className="section-heading">
          <div>
            <span className="section-kicker dark">Acompanhamento</span>
            <h2>Análises recentes</h2>
          </div>
        </div>
        {recent.length ? (
          <div className="case-table">
            {recent.map(item => (
              <div className="case-row" key={item.id}>
                <span className="case-signal">{item.modalityName}</span>
                <div><strong>{item.recordCode}</strong><span>{formatDate(item.createdAt)}</span></div>
                <div><strong>{item.primaryFinding}</strong><span>{item.status}</span></div>
                <span className="quality-pill">Qualidade {item.inspection.quality}%</span>
              </div>
            ))}
          </div>
        ) : <EmptyState onStart={onStart} />}
      </section>
    </div>
  );
}

function AnalysisPage({ modality, onModality, signal, fileName, sampleRate, onSampleRate, quality, inputRef, onFile, onDemo, recordCode, onRecordCode, selectedSymptoms, onSymptom, notes, onNotes, result, busy, error, acknowledged, onAcknowledged, onAnalyze, onSave }) {
  return (
    <div className="page analysis-page">
      <div className="page-title-row">
        <div>
          <span className="section-kicker dark">Fluxo orientado</span>
          <h1>Nova análise de sinal</h1>
          <p>Preencha apenas informações desidentificadas e revise cada etapa antes de gerar a pré-análise.</p>
        </div>
        <div className="step-indicator"><span className="active">1</span><i /><span className={signal.length ? "active" : ""}>2</span><i /><span className={result ? "active" : ""}>3</span></div>
      </div>

      <section className="analysis-layout">
        <div className="analysis-main">
          <article className="panel">
            <div className="panel-heading">
              <div><span className="step-number">01</span><h2>Modalidade do exame</h2></div>
              <small>Selecione o tipo de sinal</small>
            </div>
            <div className="modality-selector">
              {modalities.map(item => (
                <button key={item.id} className={modality.id === item.id ? "selected" : ""} onClick={() => onModality(item)}>
                  <span style={{ background: item.color }} />
                  <strong>{item.name}</strong>
                  <small>{item.target}</small>
                </button>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div><span className="step-number">02</span><h2>Sinal fisiológico</h2></div>
              <small>CSV, TXT ou JSON · máximo de 20.000 amostras</small>
            </div>
            {!signal.length ? (
              <div className="upload-zone" onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); onFile(event.dataTransfer.files[0]); }}>
                <input ref={inputRef} type="file" accept=".csv,.txt,.json" onChange={event => onFile(event.target.files?.[0])} />
                <div className="upload-symbol"><span>+</span></div>
                <h3>Arraste o arquivo do sinal para esta área</h3>
                <p>O arquivo deve conter amostras numéricas em uma coluna ou vetor.</p>
                <div className="upload-actions">
                  <button className="button primary" onClick={() => inputRef.current?.click()}>Selecionar arquivo</button>
                  <button className="button secondary" onClick={onDemo}>Usar amostra demonstrativa</button>
                </div>
              </div>
            ) : (
              <div className="signal-loaded">
                <div className="signal-toolbar">
                  <div><span className="file-dot" style={{ background: modality.color }} /><strong>{fileName}</strong><small>{signal.length.toLocaleString("pt-BR")} amostras</small></div>
                  <button className="text-button" onClick={() => inputRef.current?.click()}>Substituir arquivo</button>
                  <input ref={inputRef} type="file" accept=".csv,.txt,.json" onChange={event => onFile(event.target.files?.[0])} />
                </div>
                <Waveform signal={signal} color={modality.color} />
                <div className="signal-meta">
                  <label>Frequência de amostragem<input type="number" min="20" max="10000" value={sampleRate} onChange={event => onSampleRate(Number(event.target.value))} /><span>Hz</span></label>
                  <div><span>Canal</span><strong>{modality.channel}</strong></div>
                  <div><span>Duração</span><strong>{quality?.duration.toFixed(2)} s</strong></div>
                  <div><span>Unidade</span><strong>{modality.unit}</strong></div>
                </div>
              </div>
            )}
            {error && <div className="error-message">{error}</div>}
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div><span className="step-number">03</span><h2>Contexto para revisão</h2></div>
              <small>Não informe nome, CPF, prontuário ou contato</small>
            </div>
            <div className="form-grid">
              <label className="field"><span>Código anonimizado do caso</span><input value={recordCode} onChange={event => onRecordCode(event.target.value)} maxLength={32} /></label>
              <label className="field"><span>Modelo de análise</span><select><option>{modality.name}-demo 0.4 · acadêmico</option></select></label>
            </div>
            <fieldset className="symptom-fieldset">
              <legend>Sinais e sintomas relatados</legend>
              <div className="chip-list">
                {symptoms.map(symptom => <button type="button" key={symptom} className={selectedSymptoms.includes(symptom) ? "chip selected" : "chip"} onClick={() => onSymptom(symptom)}>{selectedSymptoms.includes(symptom) ? "✓ " : "+ "}{symptom}</button>)}
              </div>
            </fieldset>
            <label className="field notes-field"><span>Observações clínicas desidentificadas</span><textarea value={notes} onChange={event => onNotes(event.target.value)} placeholder="Registre informações relevantes para a discussão do caso." /></label>
          </article>
        </div>

        <aside className="analysis-side">
          <article className="panel sticky-panel">
            <div className="side-heading"><span>Controle de qualidade</span><span className={quality ? `quality-state ${quality.status.toLowerCase()}` : "quality-state"}>{quality?.status || "Aguardando sinal"}</span></div>
            {quality ? (
              <>
                <div className="quality-summary"><Ring value={quality.quality} label="qualidade" /><p>{quality.message}</p></div>
                <div className="quality-list">
                  <div><span>Amostras válidas</span><strong>{quality.samples.toLocaleString("pt-BR")}</strong></div>
                  <div><span>Ruído relativo</span><strong>{(quality.noiseRatio * 100).toFixed(1)}%</strong></div>
                  <div><span>Saturação</span><strong>{(quality.clipping * 100).toFixed(1)}%</strong></div>
                  <div><span>Faixa dinâmica</span><strong>{quality.dynamicRange.toFixed(2)}</strong></div>
                </div>
              </>
            ) : (
              <div className="side-empty"><span>∿</span><p>Envie um sinal para verificar duração, ruído, saturação e faixa dinâmica.</p></div>
            )}
            <label className="consent-check"><input type="checkbox" checked={acknowledged} onChange={event => onAcknowledged(event.target.checked)} /><p>Utilizarei o resultado somente para ensino ou pesquisa, com revisão de profissional habilitado.</p></label>
            <button className="button primary full" disabled={!signal.length || busy || quality?.status === "Insuficiente" || !acknowledged} onClick={onAnalyze}>{busy ? "Processando sinal..." : "Gerar pré-análise"}</button>
            <small className="button-note">Nenhuma decisão clínica deve ser tomada apenas com esta saída.</small>
          </article>
        </aside>
      </section>

      {result && <Results result={result} modality={modality} signal={signal} onSave={onSave} />}
    </div>
  );
}

function Results({ result, modality, signal, onSave }) {
  return (
    <section className="results-section" id="results">
      <div className="results-header">
        <div>
          <span className="section-kicker">Resultado para revisão</span>
          <h2>Pré-análise concluída</h2>
          <p>{result.id} · {formatDate(result.createdAt)}</p>
        </div>
        <div className="result-actions">
          <button className="button light-outline" onClick={onSave}>Salvar caso</button>
          <button className="button light-outline" onClick={() => downloadJson(result, `${result.id}.json`)}>Exportar JSON</button>
          <button className="button light" onClick={() => window.print()}>Gerar relatório</button>
        </div>
      </div>
      {result.urgentContext && <div className="clinical-alert"><strong>Contexto prioritário para avaliação</strong><span>Há sinal ou sintoma de alarme informado. Aplique o protocolo assistencial institucional, independentemente da classificação do modelo.</span></div>}
      <div className="result-grid">
        <article className="result-card main-finding">
          <span className="result-label">Classe priorizada pelo modelo</span>
          <h3>{result.primaryFinding}</h3>
          <p>Resultado exploratório que deve ser confrontado com o traçado completo e os dados clínicos.</p>
          <div className="finding-metrics">
            <Ring value={result.confidence} label="probabilidade" tone="light" />
            <div><span>Incerteza</span><strong>{result.uncertainty}</strong><small>Modelo demonstrativo</small></div>
            <div><span>Qualidade</span><strong>{result.inspection.quality}%</strong><small>{result.inspection.status}</small></div>
          </div>
          <div className="result-wave"><Waveform signal={signal} color="#ffffff" /></div>
        </article>
        <article className="result-card probability-card">
          <div className="card-title"><div><span className="result-label">Distribuição</span><h3>Hipóteses do modelo</h3></div><span className="demo-badge">{result.status}</span></div>
          <div className="probability-list">
            {result.probabilities.map((item, index) => (
              <div key={item.label}>
                <div><span><i>{index + 1}</i>{item.label}</span><strong>{Math.round(item.value * 100)}%</strong></div>
                <div className="bar"><span style={{ width: `${item.value * 100}%`, background: index === 0 ? modality.color : "#afbbb8" }} /></div>
              </div>
            ))}
          </div>
          <small>{result.status === "Simulação acadêmica" ? "Probabilidades demonstrativas, sem calibração clínica. Não representam prevalência ou risco individual." : "Consulte o cartão do modelo para métricas de calibração, população avaliada e limitações."}</small>
        </article>
        <article className="result-card explanation-card">
          <span className="result-label">Interpretabilidade</span>
          <h3>{result.status === "Simulação acadêmica" ? "Características examinadas na simulação" : "Características que influenciaram a saída"}</h3>
          <div className="feature-list">
            {result.features.map(feature => (
              <div key={feature.name}>
                <div><span>{feature.name}</span><strong>{feature.value}%</strong></div>
                <div className="feature-track"><span style={{ width: `${feature.value}%` }} /></div>
                <small>{feature.direction}</small>
              </div>
            ))}
          </div>
        </article>
        <article className="result-card review-card">
          <span className="result-label">Síntese para discussão clínica</span>
          <h3>Próximas verificações</h3>
          <ol>
            {result.recommendations.map(item => <li key={item}>{item}</li>)}
          </ol>
          <div className="model-card-note"><strong>{result.model}</strong><span>Não validado para diagnóstico, prognóstico ou conduta terapêutica.</span></div>
        </article>
      </div>
    </section>
  );
}

function CasesPage({ history, onStart, onClear }) {
  return (
    <div className="page">
      <div className="page-title-row">
        <div><span className="section-kicker dark">Registro desta sessão</span><h1>Casos analisados</h1><p>Somente códigos anonimizados são exibidos. O histórico permanece neste navegador.</p></div>
        <div className="page-actions"><button className="button secondary" onClick={onClear} disabled={!history.length}>Limpar histórico</button><button className="button primary" onClick={onStart}>Nova análise</button></div>
      </div>
      {history.length ? (
        <div className="cases-grid">
          {history.map(item => (
            <article className="saved-case" key={item.id}>
              <div className="saved-case-head"><span className="case-signal">{item.modalityName}</span><span>{formatDate(item.createdAt)}</span></div>
              <h3>{item.recordCode}</h3>
              <p>{item.primaryFinding}</p>
              <div className="saved-case-metrics"><span>Probabilidade <strong>{item.confidence}%</strong></span><span>Qualidade <strong>{item.inspection.quality}%</strong></span></div>
              <div className="saved-case-foot"><span>{item.status}</span><button onClick={() => downloadJson(item, `${item.id}.json`)}>Exportar</button></div>
            </article>
          ))}
        </div>
      ) : <EmptyState onStart={onStart} />}
    </div>
  );
}
