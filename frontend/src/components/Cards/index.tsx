import { useCallback, useEffect, useRef, useState } from 'react';
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

export function Card() {
    const [stats, setStats] = useState<StatsData | null>(null);
    const [loading, setLoading] = useState(true);
    const requestInFlightRef = useRef(false);
    const pendingRefetchRef = useRef(false);
    const lastRealtimeSyncRef = useRef(0);

    const fetchStats = useCallback(async () => {
        if (requestInFlightRef.current) {
            pendingRefetchRef.current = true;
            return;
        }

        requestInFlightRef.current = true;
        try {
            const [statsResponse, snifferResponse] = await Promise.allSettled([
                api.get('/service/stats'),
                api.get('/sniffer/status'),
            ]);

            if (statsResponse.status === 'fulfilled') {
                setStats(statsResponse.value.data);
            }

            if (snifferResponse.status === 'fulfilled') {
                setSnifferStatus({
                    running: !!snifferResponse.value.data?.running,
                    anomalias: Number(snifferResponse.value.data?.anomalias || 0),
                    taxa_anomalia: Number(snifferResponse.value.data?.taxa_anomalia || 0),
                });
            }

            if (statsResponse.status === 'rejected' && snifferResponse.status === 'rejected') {
                console.error('Erro ao buscar stats:', statsResponse.reason || snifferResponse.reason);
            }
        } catch (error) {
            console.error('Erro ao buscar stats:', error);
        } finally {
            requestInFlightRef.current = false;
            setLoading(false);

            // Se eventos chegaram durante a requisição atual, sincroniza uma vez ao final.
            if (pendingRefetchRef.current) {
                pendingRefetchRef.current = false;
                void fetchStats();
            }
        }
    }, []);

    useEffect(() => {
<<<<<<< HEAD
        const fetchStats = async () => {
            try {
                const response = await api.get('/service/stats');
                setStats(response.data);
            } catch (error) {
                console.error('Erro ao buscar stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        // Atualiza a cada 30 segundos
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);
=======
        void fetchStats();
        const interval = setInterval(() => {
            void fetchStats();
        }, 30000);

        const onSnifferUpdate = () => {
            const now = Date.now();
            if (now - lastRealtimeSyncRef.current < 5000) {
                return;
            }
            lastRealtimeSyncRef.current = now;
            void fetchStats();
        };

        window.addEventListener('sniffer:update', onSnifferUpdate);
        return () => {
            clearInterval(interval);
            window.removeEventListener('sniffer:update', onSnifferUpdate);
        };
    }, [fetchStats]);
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7

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
                    <CardNum>{Number(stats?.throughput_mbps ?? 0).toFixed(2)}</CardNum>
                    <CardSubtitle>Mbps</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>INTEGRIDADE DO TRAFEGO</CardTitle>
                <CardInfo>
                    <CardNum $isActive={stats?.sistema_ativo === true}>
                        {stats?.sistema_ativo === true ? '✓ ATIVO' : '✗ INATIVO'}
                    </CardNum>
                    <CardSubtitle>{stats?.sistema_ativo === true ? 'Monitorando' : 'Verificar'}</CardSubtitle>
                </CardInfo>
            </CardContent>
        </CardContainer>
    )
}