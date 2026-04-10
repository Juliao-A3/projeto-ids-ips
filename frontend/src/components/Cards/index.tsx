import { useEffect, useState } from 'react';
import {
    CardContainer,
    CardContent,
    CardTitle,
    CardInfo,
    CardNum,
    CardSubtitle
} from './styles'
import { api } from '../../services/api';

interface StatsData {
    alertas: number;
    bloqueios: number;
    throughput_mbps: number;
    sistema_ativo?: boolean;
}

interface SnifferStatusData {
    running: boolean;
    anomalias: number;
    taxa_anomalia: number;
}

export function Card() {
    const [stats, setStats] = useState<StatsData | null>(null);
    const [snifferStatus, setSnifferStatus] = useState<SnifferStatusData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const [statsResponse, snifferResponse] = await Promise.all([
                    api.get('/service/stats'),
                    api.get('/sniffer/status'),
                ]);
                setStats(statsResponse.data);
                setSnifferStatus({
                    running: !!snifferResponse.data?.running,
                    anomalias: Number(snifferResponse.data?.anomalias || 0),
                    taxa_anomalia: Number(snifferResponse.data?.taxa_anomalia || 0),
                });
            } catch (error) {
                console.error('Erro ao buscar stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 30000);
        const onSnifferUpdate = () => {
            fetchStats();
        };

        window.addEventListener('sniffer:update', onSnifferUpdate);
        return () => {
            clearInterval(interval);
            window.removeEventListener('sniffer:update', onSnifferUpdate);
        };
    }, []);

    const attackDetected = (snifferStatus?.anomalias || 0) > 0;
    const captureRunning = !!snifferStatus?.running;
    const anomalyRate = Math.max(0, Math.min(100, Number(snifferStatus?.taxa_anomalia || 0)));
    const integrityPercentage = captureRunning ? Math.max(0, 100 - anomalyRate) : 0;
    const integrityLabel = !captureRunning
        ? 'Captura parada'
        : (anomalyRate >= 20 || attackDetected)
            ? 'Crítico'
            : anomalyRate >= 5
                ? 'Atenção'
                : 'Estável';

    if (loading) {
        return (
            <CardContainer>
                <CardContent>
                    <CardTitle>Carregando...</CardTitle>
                </CardContent>
            </CardContainer>
        );
    }

    return (
        <CardContainer>
            <CardContent>
                <CardTitle>Alertas Totais(24H)</CardTitle>
                <CardInfo>
                    <CardNum>{stats?.alertas || 0}</CardNum>
                    <CardSubtitle>Monitorado</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>ATAQUES BLOQUEADOS</CardTitle>
                <CardInfo>
                    <CardNum>{stats?.bloqueios || 0}</CardNum>
                    <CardSubtitle>Bloqueios Ativos</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>THROUGHPUT</CardTitle>
                <CardInfo>
                    <CardNum>{stats?.throughput_mbps.toFixed(2) || '0.00'}</CardNum>
                    <CardSubtitle>Mbps</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>INTEGRIDADE DO TRAFEGO</CardTitle>
                <CardInfo>
                    <CardNum $isActive={captureRunning}>
                        {captureRunning ? `${integrityPercentage.toFixed(1)}%` : '0.0%'}
                    </CardNum>
                    <CardSubtitle>
                        {captureRunning ? `${integrityLabel} (${anomalyRate.toFixed(1)}% anomalia)` : integrityLabel}
                    </CardSubtitle>
                </CardInfo>
            </CardContent>
        </CardContainer>
    )
}