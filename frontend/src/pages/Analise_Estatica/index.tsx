import {
  Container, Title, Grid, Card, CardTitle, DropZone, DropText,
  Label, Input, Btn, Select, StatCard, StatValue, StatLabel,
  FullCard, Table, Th, Td, Badge, ErrorMsg,
} from './styles';
import { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, FileText, Download, FolderOpen, RefreshCw, Table2 } from 'lucide-react';
import { useAnaliseEstatica } from '../../../hooks/useAnáliseEstatica';
import { api } from '../../services/api';

// ── tipo de resultado CSV
interface ResultadoCSV {
  ficheiro: string;
  total_linhas: number;
  normais: number;
  anomalias: number;
  taxa_anomalia: number;
  pacotes: any[];
}

export function AnaliseEstatica() {
  const {
    loading, resultado, historico, testeAtual, error,
    testarUpload, testarPasta, fetchHistorico, exportarCSV,
  } = useAnaliseEstatica();

  const [ficheiro, setFicheiro]         = useState<File | null>(null);
  const [dragging, setDragging]         = useState(false);
  const [modeloSel, setModeloSel]       = useState('');
  const [limite, setLimite]             = useState('5000');
  const [pastaSel, setPastaSel]         = useState('ambas');
  const [tipoFicheiro, setTipoFicheiro] = useState<'pcap' | 'csv'>('pcap');

  // CSV próprio
  const [csvLoading, setCsvLoading]     = useState(false);
  const [csvError, setCsvError]         = useState('');
  const [resultadoCSV, setResultadoCSV] = useState<ResultadoCSV | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { fetchHistorico(); }, []);

  // ── drag & drop (pcap + csv)
  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (!f) return;
    const nome = f.name.toLowerCase();
    if (nome.endsWith('.pcap') || nome.endsWith('.pcapng')) {
      setFicheiro(f);
      setTipoFicheiro('pcap');
      setResultadoCSV(null);
    } else if (nome.endsWith('.csv')) {
      setFicheiro(f);
      setTipoFicheiro('csv');
      setResultadoCSV(null);
    }
  }, []);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    if (!f) return;
    const nome = f.name.toLowerCase();
    if (nome.endsWith('.csv')) {
      setTipoFicheiro('csv');
      setResultadoCSV(null);
    } else {
      setTipoFicheiro('pcap');
      setResultadoCSV(null);
    }
    setFicheiro(f);
  };

  // ── analisar PCAP (comportamento original)
  const handleAnalisarPCAP = async () => {
    if (!ficheiro) return;
    await testarUpload(ficheiro, modeloSel || undefined, parseInt(limite));
  };

  // ── analisar CSV
  const handleAnalisarCSV = async () => {
    if (!ficheiro) return;
    setCsvLoading(true);
    setCsvError('');
    setResultadoCSV(null);
    try {
      const form = new FormData();
      form.append('ficheiro', ficheiro);
      if (modeloSel) form.append('modelo', modeloSel);
      const res = await api.post('/testar/upload-csv', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResultadoCSV(res.data);
    } catch (err: any) {
      setCsvError(err.response?.data?.detail || 'Erro ao analisar CSV');
    } finally {
      setCsvLoading(false);
    }
  };

  const handleAnalisar = () =>
    tipoFicheiro === 'csv' ? handleAnalisarCSV() : handleAnalisarPCAP();

  const isLoading = loading || csvLoading;

  // ── exportar CSV do resultado CSV
  const handleExportarCSV = () => {
    if (tipoFicheiro === 'csv' && resultadoCSV) {
      exportarCSV(resultadoCSV.pacotes || []);
    } else if (resultado) {
      exportarCSV(resultado.resultado?.pacotes || []);
    }
  };

  const temResultado = tipoFicheiro === 'csv' ? !!resultadoCSV : !!resultado;

  // ── dados do resultado para os StatCards
  const statsResultado = tipoFicheiro === 'csv' && resultadoCSV
    ? {
        ficheiro:      resultadoCSV.ficheiro,
        total_pacotes: resultadoCSV.total_linhas,
        normais:       resultadoCSV.normais,
        anomalias:     resultadoCSV.anomalias,
        taxa_anomalia: resultadoCSV.taxa_anomalia,
      }
    : resultado
    ? {
        ficheiro:      resultado.ficheiro,
        total_pacotes: resultado.resultado?.total_pacotes || 0,
        normais:       resultado.resultado?.normais || 0,
        anomalias:     resultado.resultado?.anomalias || 0,
        taxa_anomalia: resultado.resultado?.taxa_anomalia || 0,
      }
    : null;

  return (
    <Container>
      <Title>ANÁLISE ESTÁTICA</Title>

      {(error || csvError) && <ErrorMsg>⚠ {error || csvError}</ErrorMsg>}

      <Grid>
        {/* ── Upload PCAP / CSV ── */}
        <Card>
          <CardTitle>UPLOAD DE FICHEIRO</CardTitle>

          <DropZone
            $active={dragging}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => fileRef.current?.click()}
          >
            {tipoFicheiro === 'csv'
              ? <Table2 size={32} color={dragging ? '#00A3FF' : '#64748B'} />
              : <Upload  size={32} color={dragging ? '#00A3FF' : '#64748B'} />
            }
            <DropText>
              {ficheiro
                ? `✓ ${ficheiro.name}`
                : 'Arrasta um ficheiro .pcap, .pcapng ou .csv aqui, ou clica para selecionar'
              }
            </DropText>

            {/* badge do tipo detetado */}
            {ficheiro && (
              <div style={{
                marginTop: 8,
                display: 'inline-block',
                padding: '2px 10px',
                borderRadius: 4,
                fontSize: 9,
                fontFamily: "'Share Tech Mono', monospace",
                letterSpacing: 1,
                background: tipoFicheiro === 'csv' ? 'rgba(168,85,247,0.15)' : 'rgba(0,163,255,0.15)',
                border: `1px solid ${tipoFicheiro === 'csv' ? 'rgba(168,85,247,0.4)' : 'rgba(0,163,255,0.4)'}`,
                color: tipoFicheiro === 'csv' ? '#A855F7' : '#00A3FF',
              }}>
                {tipoFicheiro === 'csv' ? 'CSV — FEATURES' : 'PCAP — RAW'}
              </div>
            )}
          </DropZone>

          <input
            ref={fileRef}
            type="file"
            accept=".pcap,.pcapng,.csv"
            style={{ display: 'none' }}
            onChange={onFileChange}
          />

          {/* dica CSV */}
          {tipoFicheiro === 'csv' && (
            <div style={{
              marginTop: 10,
              padding: '8px 12px',
              background: 'rgba(168,85,247,0.08)',
              border: '1px solid rgba(168,85,247,0.25)',
              borderRadius: 6,
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 9,
              color: '#A855F7',
              lineHeight: 1.6,
            }}>
              ℹ O CSV deve conter as 14 features extraídas pelo AEGIS.<br />
              Colunas: duration, packet_count, byte_count, src_port, dst_port,<br />
              protocol, flag_syn, flag_ack, flag_fin, flag_rst, pkt_size_mean,<br />
              pkt_size_std, inter_arrival_mean, inter_arrival_std
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <Label>MODELO (opcional)</Label>
            <Input
              placeholder="ex: best_model.pkl"
              value={modeloSel}
              onChange={e => setModeloSel(e.target.value)}
            />
            {tipoFicheiro === 'pcap' && (
              <>
                <Label>LIMITE DE PACOTES</Label>
                <Input
                  type="number"
                  value={limite}
                  onChange={e => setLimite(e.target.value)}
                />
              </>
            )}
          </div>

          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <Btn onClick={handleAnalisar} disabled={!ficheiro || isLoading}>
              {tipoFicheiro === 'csv'
                ? <Table2 size={14} />
                : <FileText size={14} />
              }
              {isLoading
                ? 'A ANALISAR...'
                : tipoFicheiro === 'csv' ? 'ANALISAR CSV' : 'ANALISAR'
              }
            </Btn>

            {temResultado && (
              <Btn $variant="success" onClick={handleExportarCSV}>
                <Download size={14} /> EXPORTAR CSV
              </Btn>
            )}
          </div>
        </Card>

        {/* ── Testar Pastas ── */}
        <Card>
          <CardTitle>TESTAR COM PASTAS</CardTitle>

          <Label>PASTA</Label>
          <Select value={pastaSel} onChange={e => setPastaSel(e.target.value)}>
            <option value="ambas">Ambas (Normal + Ataques)</option>
            <option value="normal">Só Normal</option>
            <option value="attacks">Só Ataques</option>
          </Select>

          <Label>MODELO (opcional)</Label>
          <Input
            placeholder="ex: best_model.pkl"
            value={modeloSel}
            onChange={e => setModeloSel(e.target.value)}
          />

          <Label>LIMITE DE PACOTES POR PCAP</Label>
          <Input
            type="number"
            value={limite}
            onChange={e => setLimite(e.target.value)}
          />

          <Btn onClick={async () => { await testarPasta(pastaSel, modeloSel || undefined, parseInt(limite)); setTimeout(fetchHistorico, 2000); }} disabled={isLoading}>
            <FolderOpen size={14} />
            {isLoading ? 'A TESTAR...' : 'TESTAR PASTA'}
          </Btn>

          {testeAtual?.resultado && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 16 }}>
              <StatCard $color="#00C853">
                <StatValue $color="#00C853">{testeAtual.resultado.normais?.total_pcaps || 0}</StatValue>
                <StatLabel>PASTA NORMAL</StatLabel>
              </StatCard>
              <StatCard $color="#EF4444">
                <StatValue $color="#EF4444">{testeAtual.resultado.ataques?.total_pcaps || 0}</StatValue>
                <StatLabel>PASTA ATAQUES</StatLabel>
              </StatCard>
            </div>
          )}
        </Card>

        {/* ── Resultado ── */}
        {statsResultado && (
          <FullCard>
            <CardTitle>
              RESULTADO DA ANÁLISE —{' '}
              <span style={{ color: tipoFicheiro === 'csv' ? '#A855F7' : '#00A3FF' }}>
                {statsResultado.ficheiro}
              </span>
            </CardTitle>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
              <StatCard>
                <StatValue>{statsResultado.total_pacotes}</StatValue>
                <StatLabel>{tipoFicheiro === 'csv' ? 'TOTAL LINHAS' : 'TOTAL PACOTES'}</StatLabel>
              </StatCard>
              <StatCard $color="#00C853">
                <StatValue $color="#00C853">{statsResultado.normais}</StatValue>
                <StatLabel>NORMAIS</StatLabel>
              </StatCard>
              <StatCard $color="#EF4444">
                <StatValue $color="#EF4444">{statsResultado.anomalias}</StatValue>
                <StatLabel>ANOMALIAS</StatLabel>
              </StatCard>
              <StatCard $color="#FFAB00">
                <StatValue $color="#FFAB00">
                  {statsResultado.taxa_anomalia?.toFixed(1) || 0}%
                </StatValue>
                <StatLabel>TAXA ANOMALIA</StatLabel>
              </StatCard>
            </div>
          </FullCard>
        )}

        {/* ── Histórico ── */}
        <FullCard>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <CardTitle style={{ margin: 0 }}>HISTÓRICO DE TESTES</CardTitle>
            <Btn onClick={fetchHistorico} style={{ padding: '6px 12px' }}>
              <RefreshCw size={12} /> ATUALIZAR
            </Btn>
          </div>

          {historico.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#64748B', fontFamily: "'Share Tech Mono', monospace", fontSize: 11, padding: 20 }}>
              Nenhum teste registado ainda.
            </div>
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>DATA</Th>
                  <Th>MODELO</Th>
                  <Th>TIPO</Th>
                  <Th>NORMAIS</Th>
                  <Th>ATAQUES</Th>
                  <Th>TOTAL</Th>
                </tr>
              </thead>
              <tbody>
                {historico.map((h, i) => (
                  <tr key={i}>
                    <Td>{h.data_teste?.slice(0, 16).replace('T', ' ')}</Td>
                    <Td>{h.modelo}</Td>
                    <Td>
                      <Badge $color={h.tipo === 'csv' ? '#A855F7' : '#00A3FF'}>
                        {h.tipo?.toUpperCase() || 'PCAP'}
                      </Badge>
                    </Td>
                    <Td><Badge $color="#00C853">{h.n_normais}</Badge></Td>
                    <Td><Badge $color="#EF4444">{h.n_ataques}</Badge></Td>
                    <Td>{h.total_pcaps}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </FullCard>
      </Grid>
    </Container>
  );
}