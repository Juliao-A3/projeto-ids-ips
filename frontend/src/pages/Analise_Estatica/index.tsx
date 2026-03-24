import {
  Container, Title, Grid, Card, CardTitle, DropZone, DropText,
  Label, Input, Btn, Select, StatCard, StatValue, StatLabel,
  FullCard, Table, Th, Td, Badge, ErrorMsg,
} from './styles';
import { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, FileText, Download, FolderOpen, RefreshCw } from 'lucide-react';
import { useAnaliseEstatica } from '../../../hooks/useAnáliseEstatica';

export function AnaliseEstatica() {
  const {
    loading, resultado, historico, testeAtual, error,
    testarUpload, testarPasta, fetchHistorico, exportarCSV,
  } = useAnaliseEstatica();

  const [ficheiro, setFicheiro]   = useState<File | null>(null);
  const [dragging, setDragging]   = useState(false);
  const [modeloSel, setModeloSel] = useState('');
  const [limite, setLimite]       = useState('5000');
  const [pastaSel, setPastaSel]   = useState('ambas');
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { fetchHistorico(); }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.name.endsWith('.pcap') || f.name.endsWith('.pcapng'))) {
      setFicheiro(f);
    }
  }, []);

  const handleAnalisar = async () => {
    if (!ficheiro) return;
    await testarUpload(ficheiro, modeloSel || undefined, parseInt(limite));
  };

  const handleTestarPasta = async () => {
    await testarPasta(pastaSel, modeloSel || undefined, parseInt(limite));
    setTimeout(fetchHistorico, 2000);
  };

  return (
    <Container>
      <Title>ANÁLISE ESTÁTICA</Title>

      {error && <ErrorMsg>⚠ {error}</ErrorMsg>}

      <Grid>
        {/* Upload PCAP */}
        <Card>
          <CardTitle>UPLOAD DE PCAP</CardTitle>

          <DropZone
            $active={dragging}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => fileRef.current?.click()}
          >
            <Upload size={32} color={dragging ? '#00A3FF' : '#64748B'} />
            <DropText>
              {ficheiro
                ? `✓ ${ficheiro.name}`
                : 'Arrasta um ficheiro .pcap ou .pcapng aqui, ou clica para selecionar'
              }
            </DropText>
          </DropZone>
          <input
            ref={fileRef}
            type="file"
            accept=".pcap,.pcapng"
            style={{ display: 'none' }}
            onChange={e => setFicheiro(e.target.files?.[0] || null)}
          />

          <div style={{ marginTop: 16 }}>
            <Label>MODELO (opcional)</Label>
            <Input
              placeholder="ex: best_model.pkl"
              value={modeloSel}
              onChange={e => setModeloSel(e.target.value)}
            />
            <Label>LIMITE DE PACOTES</Label>
            <Input
              type="number"
              value={limite}
              onChange={e => setLimite(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <Btn onClick={handleAnalisar} disabled={!ficheiro || loading}>
              <FileText size={14} />
              {loading ? 'A ANALISAR...' : 'ANALISAR'}
            </Btn>
            {resultado && (
              <Btn
                $variant="success"
                onClick={() => exportarCSV(resultado.resultado?.pacotes || [])}
              >
                <Download size={14} /> EXPORTAR CSV
              </Btn>
            )}
          </div>
        </Card>

        {/* Testar Pastas */}
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

          <Btn onClick={handleTestarPasta} disabled={loading}>
            <FolderOpen size={14} />
            {loading ? 'A TESTAR...' : 'TESTAR PASTA'}
          </Btn>

          {/* Cards das pastas */}
          {testeAtual?.resultado && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 16 }}>
              <StatCard $color="#00C853">
                <StatValue $color="#00C853">
                  {testeAtual.resultado.normais?.total_pcaps || 0}
                </StatValue>
                <StatLabel>PASTA NORMAL</StatLabel>
              </StatCard>
              <StatCard $color="#EF4444">
                <StatValue $color="#EF4444">
                  {testeAtual.resultado.ataques?.total_pcaps || 0}
                </StatValue>
                <StatLabel>PASTA ATAQUES</StatLabel>
              </StatCard>
            </div>
          )}
        </Card>

        {/* Resultado do Upload */}
        {resultado && (
          <FullCard>
            <CardTitle>RESULTADO DA ANÁLISE — {resultado.ficheiro}</CardTitle>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
              <StatCard>
                <StatValue>{resultado.resultado?.total_pacotes || 0}</StatValue>
                <StatLabel>TOTAL PACOTES</StatLabel>
              </StatCard>
              <StatCard $color="#00C853">
                <StatValue $color="#00C853">{resultado.resultado?.normais || 0}</StatValue>
                <StatLabel>NORMAIS</StatLabel>
              </StatCard>
              <StatCard $color="#EF4444">
                <StatValue $color="#EF4444">{resultado.resultado?.anomalias || 0}</StatValue>
                <StatLabel>ANOMALIAS</StatLabel>
              </StatCard>
              <StatCard $color="#FFAB00">
                <StatValue $color="#FFAB00">
                  {resultado.resultado?.taxa_anomalia?.toFixed(1) || 0}%
                </StatValue>
                <StatLabel>TAXA ANOMALIA</StatLabel>
              </StatCard>
            </div>
          </FullCard>
        )}

        {/* Histórico */}
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
                  <Th>NORMAIS</Th>
                  <Th>ATAQUES</Th>
                  <Th>TOTAL PCAPs</Th>
                </tr>
              </thead>
              <tbody>
                {historico.map((h, i) => (
                  <tr key={i}>
                    <Td>{h.data_teste?.slice(0, 16).replace('T', ' ')}</Td>
                    <Td>{h.modelo}</Td>
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