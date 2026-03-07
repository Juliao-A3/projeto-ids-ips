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

export function Card() {
    const [stats, setStats] = useState<StatsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
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
                    <CardNum $isActive={stats?.sistema_ativo === true}>
                        {stats?.sistema_ativo === true ? '✓ ATIVO' : '✗ INATIVO'}
                    </CardNum>
                    <CardSubtitle>{stats?.sistema_ativo === true ? 'Monitorando' : 'Verificar'}</CardSubtitle>
                </CardInfo>
            </CardContent>
        </CardContainer>
    )
}