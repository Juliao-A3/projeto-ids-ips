import {
  Container, Title, Grid, Card, FullCard, CardTitle,
  InfoRow, InfoLabel, InfoValue, AccuracyBar, AccuracyFill,
  Label, Select, InputNum, Btn, ProgressBar, ProgressFill,
  FeatureList, FeatureItem, Table, Th, Td, Badge,
  ErrorMsg,
} from './styles';
import { useState } from 'react';
import { Brain, RefreshCw, Search, Play, CheckCircle } from 'lucide-react';
import { useGestaoIA } from '../../../hooks/useGestaoIA';
import { api } from '../../services/api';

export function GestaoIA() {
  const {
    modelo, modelos, estatisticas, treino, inspecao,
    loading, treinando, error,
    fetchModelo, fetchEstatisticas, inspecionarModelo, iniciarTreino,
  } = useGestaoIA();

  const [modeloInsp, setModeloInsp]     = useState('');
  const [ativando, setAtivando]         = useState(false);
  const [ativarMsg, setAtivarMsg]       = useState('');
  const [treinarConfig, setTreinarConfig] = useState({
    origem:        'logs',
    contamination: 0.15,
    test_size:     0.25,
    max_amostras:  5000,
  });

  const acuracia = modelo?.acuracia
    ? Math.round(modelo.acuracia * 100)
    : estatisticas?.modelo?.acuracia
    ? Math.round(estatisticas.modelo.acuracia * 100)
    : 0;

  const handleAtivarModelo = async () => {
    const nomeModelo = modeloInsp || inspecao?.nome;
    if (!nomeModelo) return;
    try {
      setAtivando(true);
      setAtivarMsg('');
      await api.post('/sniffer/modelo/ativar', { nome: nomeModelo });
      setAtivarMsg(`✓ Modelo ${nomeModelo} ativado com sucesso!`);
      fetchModelo();
      setTimeout(() => setAtivarMsg(''), 4000);
    } catch (err: any) {
      setAtivarMsg(`⚠ ${err.response?.data?.detail || 'Erro ao ativar modelo'}`);
    } finally {
      setAtivando(false);
    }
  };

  return (
    <Container>
      <Title>GESTÃO DE IA</Title>

      {error && <ErrorMsg>⚠ {error}</ErrorMsg>}

      <Grid>
        {/* ── Modelo Atual ── */}
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <CardTitle style={{ margin: 0 }}>MODELO ATUAL</CardTitle>
            <Btn $variant="outline" onClick={fetchModelo} style={{ padding: '4px 10px', fontSize: 9 }}>
              <RefreshCw size={10} /> ATUALIZAR
            </Btn>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{
              width: 48, height: 48, borderRadius: '50%',
              background: 'rgba(0,163,255,0.1)', border: '1px solid rgba(0,163,255,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Brain size={22} color="#00A3FF" />
            </div>
            <div>
              <div style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: 16, fontWeight: 700, color: '#fff' }}>
                {modelo?.nome || 'Nenhum modelo carregado'}
              </div>
              <div style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 9, color: '#64748B' }}>
                {modelo?.tipo || '—'}
              </div>
            </div>
          </div>

          <InfoRow>
            <InfoLabel>ACURÁCIA</InfoLabel>
            <InfoValue style={{ color: '#00C853' }}>{acuracia}%</InfoValue>
          </InfoRow>
          <AccuracyBar>
            <AccuracyFill $pct={acuracia} />
          </AccuracyBar>

          <InfoRow>
            <InfoLabel>DATA DE TREINO</InfoLabel>
            <InfoValue>{modelo?.data_treino?.slice(0, 10) || '—'}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>FEATURES</InfoLabel>
            <InfoValue>{modelo?.n_features || 0}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>VERSÃO</InfoLabel>
            <InfoValue>{modelo?.versao || '—'}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>TAMANHO</InfoLabel>
            <InfoValue>{estatisticas?.modelo?.tamanho_kb || 0} KB</InfoValue>
          </InfoRow>
        </Card>

        {/* ── Treinar Novo Modelo ── */}
        <Card>
          <CardTitle>TREINAR NOVO MODELO</CardTitle>

          <Label>ORIGEM DOS DADOS</Label>
          <Select
            value={treinarConfig.origem}
            onChange={e => setTreinarConfig(p => ({ ...p, origem: e.target.value }))}
          >
            <option value="logs">Logs do Sniffer</option>
            <option value="pcaps">PCAPs (data/pcaps/)</option>
          </Select>

          <Label>CONTAMINATION ({(treinarConfig.contamination * 100).toFixed(0)}%)</Label>
          <InputNum
            type="number"
            min="0.01" max="0.5" step="0.01"
            value={treinarConfig.contamination}
            onChange={e => setTreinarConfig(p => ({ ...p, contamination: parseFloat(e.target.value) }))}
          />

          <Label>DIVISÃO TESTE ({(treinarConfig.test_size * 100).toFixed(0)}%)</Label>
          <InputNum
            type="number"
            min="0.1" max="0.5" step="0.05"
            value={treinarConfig.test_size}
            onChange={e => setTreinarConfig(p => ({ ...p, test_size: parseFloat(e.target.value) }))}
          />

          <Label>MÁX. AMOSTRAS</Label>
          <InputNum
            type="number"
            value={treinarConfig.max_amostras}
            onChange={e => setTreinarConfig(p => ({ ...p, max_amostras: parseInt(e.target.value) }))}
          />

          <Btn onClick={() => iniciarTreino(treinarConfig)} disabled={treinando} $variant="success">
            <Play size={14} />
            {treinando ? 'A TREINAR...' : 'INICIAR TREINO'}
          </Btn>

          {treino && (
            <div style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 10, color: '#94A3B8' }}>
                  {treino.mensagem}
                </span>
                <span style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 10, color: '#00A3FF' }}>
                  {treino.progresso}%
                </span>
              </div>
              <ProgressBar>
                <ProgressFill $pct={treino.progresso} />
              </ProgressBar>
              {treino.acuracia && (
                <div style={{ textAlign: 'center', fontFamily: "'Share Tech Mono', monospace", fontSize: 11, color: '#00C853' }}>
                  ✓ CONCLUÍDO — Acurácia: {treino.acuracia}%
                </div>
              )}
              {treino.erro && (
                <div style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 11, color: '#EF4444' }}>
                  ⚠ {treino.erro}
                </div>
              )}
            </div>
          )}
        </Card>

        {/* ── Inspecionar + Ativar Modelo ── */}
        <Card>
          <CardTitle>INSPECIONAR MODELO</CardTitle>

          <Label>SELECIONA MODELO</Label>
          <Select value={modeloInsp} onChange={e => setModeloInsp(e.target.value)}>
            <option value="">Modelo mais recente</option>
            {modelos.map((m: any, i: number) => (
              <option key={i} value={m.nome}>{m.nome}</option>
            ))}
          </Select>

          <Btn onClick={() => inspecionarModelo(modeloInsp || undefined)} disabled={loading}>
            <Search size={14} />
            {loading ? 'A INSPECIONAR...' : 'INSPECIONAR'}
          </Btn>

          {inspecao && (
            <div style={{ marginTop: 16 }}>
              <InfoRow><InfoLabel>NOME</InfoLabel><InfoValue>{inspecao.nome}</InfoValue></InfoRow>
              <InfoRow><InfoLabel>TIPO</InfoLabel><InfoValue>{inspecao.tipo}</InfoValue></InfoRow>
              <InfoRow><InfoLabel>FEATURES</InfoLabel><InfoValue>{inspecao.n_features}</InfoValue></InfoRow>
              {inspecao.acuracia && (
                <InfoRow>
                  <InfoLabel>ACURÁCIA</InfoLabel>
                  <InfoValue style={{ color: '#00C853' }}>
                    {Math.round(inspecao.acuracia * 100)}%
                  </InfoValue>
                </InfoRow>
              )}

              {/* ── Botão Ativar ── */}
              <div style={{ marginTop: 12 }}>
                <Btn
                  onClick={handleAtivarModelo}
                  disabled={ativando}
                  $variant="success"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <CheckCircle size={14} />
                  {ativando ? 'A ATIVAR...' : 'ATIVAR ESTE MODELO'}
                </Btn>

                {ativarMsg && (
                  <div style={{
                    marginTop: 8, padding: '8px 12px',
                    background: ativarMsg.startsWith('✓')
                      ? 'rgba(0,200,83,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${ativarMsg.startsWith('✓') ? 'rgba(0,200,83,0.3)' : 'rgba(239,68,68,0.3)'}`,
                    borderRadius: 6,
                    fontFamily: "'Share Tech Mono', monospace",
                    fontSize: 10,
                    color: ativarMsg.startsWith('✓') ? '#00C853' : '#EF4444',
                    textAlign: 'center' as const,
                  }}>
                    {ativarMsg}
                  </div>
                )}

                <div style={{
                  marginTop: 6, fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 9, color: '#64748B', textAlign: 'center' as const,
                }}>
                  O modelo ativado será usado na próxima vez que o sniffer arrancar
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* ── Estatísticas Globais ── */}
        <Card>
          <CardTitle>ESTATÍSTICAS GLOBAIS</CardTitle>

          {estatisticas?.totais ? (
            <>
              <InfoRow>
                <InfoLabel>TOTAL SESSÕES</InfoLabel>
                <InfoValue>{estatisticas.totais.sessoes}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>TOTAL PACOTES</InfoLabel>
                <InfoValue>{estatisticas.totais.pacotes.toLocaleString()}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>TOTAL ANOMALIAS</InfoLabel>
                <InfoValue style={{ color: '#EF4444' }}>{estatisticas.totais.anomalias}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>TOTAL BLOQUEIOS</InfoLabel>
                <InfoValue style={{ color: '#FFAB00' }}>{estatisticas.totais.bloqueios}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>TAXA ANOMALIA</InfoLabel>
                <InfoValue style={{ color: '#EF4444' }}>{estatisticas.totais.taxa_anomalia}%</InfoValue>
              </InfoRow>
            </>
          ) : (
            <div style={{ color: '#64748B', fontFamily: "'Share Tech Mono', monospace", fontSize: 11 }}>
              Sem dados de sessões anteriores.
            </div>
          )}
        </Card>

        {/* ── Histórico de Sessões ── */}
        <FullCard>
          <CardTitle>HISTÓRICO DE SESSÕES</CardTitle>

          {(!estatisticas?.historico?.length) ? (
            <div style={{ textAlign: 'center', color: '#64748B', fontFamily: "'Share Tech Mono', monospace", fontSize: 11, padding: 20 }}>
              Nenhuma sessão registada ainda.
            </div>
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>INÍCIO</Th>
                  <Th>FIM</Th>
                  <Th>PACOTES</Th>
                  <Th>ANOMALIAS</Th>
                  <Th>BLOQUEIOS</Th>
                  <Th>IPs</Th>
                </tr>
              </thead>
              <tbody>
                {estatisticas.historico.map((s: any, i: number) => (
                  <tr key={i}>
                    <Td>{s.inicio}</Td>
                    <Td>{s.fim}</Td>
                    <Td>{s.pacotes.toLocaleString()}</Td>
                    <Td><Badge $color="#EF4444">{s.anomalias}</Badge></Td>
                    <Td><Badge $color="#FFAB00">{s.bloqueios}</Badge></Td>
                    <Td><Badge $color="#A855F7">{s.ips}</Badge></Td>
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