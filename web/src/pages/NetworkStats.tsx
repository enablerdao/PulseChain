import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Card,
  CardContent,
  Divider,
  useTheme,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  IconButton,
  Chip,
  LinearProgress
} from '@mui/material';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';
import StorageIcon from '@mui/icons-material/Storage';
import SpeedIcon from '@mui/icons-material/Speed';
import MemoryIcon from '@mui/icons-material/Memory';
import PeopleIcon from '@mui/icons-material/People';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import PublicIcon from '@mui/icons-material/Public';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js';

// ChartJSの登録
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

// 国旗のエモジ
const countryFlags: {[key: string]: string} = {
  "日本": "🇯🇵",
  "アメリカ": "🇺🇸",
  "ドイツ": "🇩🇪",
  "シンガポール": "🇸🇬",
  "カナダ": "🇨🇦",
  "イギリス": "🇬🇧",
  "フランス": "🇫🇷",
  "オーストラリア": "🇦🇺",
  "韓国": "🇰🇷",
  "中国": "🇨🇳",
  "インド": "🇮🇳",
  "ブラジル": "🇧🇷",
  "ロシア": "🇷🇺",
  "南アフリカ": "🇿🇦",
  "UAE": "🇦🇪"
};

// モックデータ生成関数
const generateMockData = () => {
  // 現在の日時
  const now = new Date();
  
  // ノード数
  const totalNodes = 1250 + Math.floor(Math.random() * 50);
  const activeNodes = totalNodes - Math.floor(Math.random() * 30);
  const validatorNodes = 500 + Math.floor(Math.random() * 20);
  
  // トランザクション数
  const dailyTx = 1200000 + Math.floor(Math.random() * 200000);
  const totalTx = 156000000 + dailyTx;
  const pendingTx = Math.floor(Math.random() * 1000);
  
  // TPS (Transactions Per Second)
  const currentTps = 10 + Math.floor(Math.random() * 5);
  const peakTps = 120;
  
  // ブロック情報
  const latestBlock = 4582000 + Math.floor(Math.random() * 100);
  const avgBlockTime = 2.5 + (Math.random() * 0.5 - 0.25);
  
  // ネットワーク情報
  const totalStaked = 500000000 + Math.floor(Math.random() * 1000000);
  const activeValidators = validatorNodes;
  
  // 地域分布
  const regionDistribution = [
    { region: "アジア", percentage: 35 + Math.floor(Math.random() * 5) },
    { region: "北米", percentage: 30 + Math.floor(Math.random() * 5) },
    { region: "ヨーロッパ", percentage: 25 + Math.floor(Math.random() * 5) },
    { region: "その他", percentage: 10 + Math.floor(Math.random() * 3) }
  ];
  
  // 調整して合計が100%になるようにする
  const total = regionDistribution.reduce((sum, item) => sum + item.percentage, 0);
  regionDistribution.forEach(item => {
    item.percentage = Math.round(item.percentage / total * 100);
  });
  
  // 過去24時間のTPSデータ
  const tpsHistory = Array.from({ length: 24 }, (_, i) => {
    return {
      hour: `${(now.getHours() - 23 + i + 24) % 24}:00`,
      tps: 5 + Math.floor(Math.random() * 15)
    };
  });
  
  // 過去7日間のトランザクション数
  const txHistory = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - 6 + i);
    return {
      date: `${date.getMonth() + 1}/${date.getDate()}`,
      count: 800000 + Math.floor(Math.random() * 400000)
    };
  });
  
  // トップバリデーター
  const topValidators = [
    { name: "PulseNode Tokyo", country: "日本", nodes: 25, uptime: 99.98, staked: 25000000 },
    { name: "Quantum Validators", country: "アメリカ", nodes: 22, uptime: 99.95, staked: 22000000 },
    { name: "Berlin Pulse", country: "ドイツ", nodes: 18, uptime: 99.92, staked: 18000000 },
    { name: "SG Validators", country: "シンガポール", nodes: 15, uptime: 99.90, staked: 15000000 },
    { name: "Maple Leaf Nodes", country: "カナダ", nodes: 12, uptime: 99.89, staked: 12000000 },
    { name: "London Bridge", country: "イギリス", nodes: 10, uptime: 99.87, staked: 10000000 },
    { name: "Paris Pulse", country: "フランス", nodes: 9, uptime: 99.85, staked: 9000000 },
    { name: "Sydney Stakers", country: "オーストラリア", nodes: 8, uptime: 99.82, staked: 8000000 },
    { name: "Seoul Secure", country: "韓国", nodes: 7, uptime: 99.80, staked: 7000000 },
    { name: "Dragon Validators", country: "中国", nodes: 6, uptime: 99.78, staked: 6000000 }
  ];
  
  return {
    timestamp: now.toISOString(),
    nodes: {
      total: totalNodes,
      active: activeNodes,
      validators: validatorNodes
    },
    transactions: {
      total: totalTx,
      daily: dailyTx,
      pending: pendingTx
    },
    performance: {
      currentTps,
      peakTps,
      tpsHistory
    },
    blocks: {
      latest: latestBlock,
      avgTime: avgBlockTime
    },
    network: {
      totalStaked,
      activeValidators,
      regionDistribution
    },
    history: {
      tps: tpsHistory,
      transactions: txHistory
    },
    topValidators
  };
};

const NetworkStats = () => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const fetchNetworkStats = async () => {
    setLoading(true);
    
    try {
      // APIからデータを取得
      const response = await fetch('http://localhost:52964/api/stats');
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setStats(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch network stats:', error);
      // エラー時はモックデータを使用
      const mockData = generateMockData();
      setStats(mockData);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchNetworkStats();
    
    // 30秒ごとに自動更新
    const interval = setInterval(() => {
      fetchNetworkStats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  // 地域分布のチャートデータ
  const regionChartData = {
    labels: stats?.network.regionDistribution.map((item: any) => item.region) || [],
    datasets: [
      {
        data: stats?.network.regionDistribution.map((item: any) => item.percentage) || [],
        backgroundColor: [
          '#4caf50', // green
          '#2196f3', // blue
          '#ff9800', // orange
          '#9c27b0'  // purple
        ],
        borderColor: isDarkMode ? '#121212' : '#ffffff',
        borderWidth: 2
      }
    ]
  };
  
  // TPS履歴のチャートデータ
  const tpsChartData = {
    labels: stats?.history.tps.map((item: any) => item.hour) || [],
    datasets: [
      {
        label: 'TPS (1時間平均)',
        data: stats?.history.tps.map((item: any) => item.tps) || [],
        borderColor: theme.palette.primary.main,
        backgroundColor: `${theme.palette.primary.main}33`,
        tension: 0.4,
        fill: true
      }
    ]
  };
  
  // トランザクション履歴のチャートデータ
  const txChartData = {
    labels: stats?.history.transactions.map((item: any) => item.date) || [],
    datasets: [
      {
        label: '日次トランザクション数',
        data: stats?.history.transactions.map((item: any) => item.count) || [],
        borderColor: theme.palette.secondary.main,
        backgroundColor: `${theme.palette.secondary.main}33`,
        tension: 0.4,
        fill: true
      }
    ]
  };
  
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: isDarkMode ? '#fff' : '#333'
        }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false
      }
    },
    scales: {
      x: {
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: isDarkMode ? '#fff' : '#333'
        }
      },
      y: {
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: isDarkMode ? '#fff' : '#333'
        }
      }
    }
  };
  
  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: isDarkMode ? '#fff' : '#333'
        }
      }
    },
    cutout: '70%'
  };
  
  // 数値のフォーマット
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ja-JP').format(num);
  };
  
  // 大きな数値のフォーマット（K, M, Bなど）
  const formatLargeNumber = (num: number) => {
    if (num >= 1000000000) {
      return `${(num / 1000000000).toFixed(2)}B`;
    }
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(2)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(2)}K`;
    }
    return num.toString();
  };

  return (
    <Box>
      {/* ヘッダーセクション */}
      <Box 
        sx={{ 
          bgcolor: 'primary.main', 
          color: 'white',
          py: 6,
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #2c3e50, #4a5568)' 
            : 'linear-gradient(135deg, #6e8efb, #a777e3)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box 
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.1,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='1' fill-rule='evenodd'/%3E%3C/svg%3E")`,
          }}
        />
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography 
              variant="h2" 
              component="h1" 
              gutterBottom
              sx={{ 
                fontWeight: 'bold',
                textShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              ネットワーク統計
            </Typography>
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              sx={{ mb: 4, maxWidth: '800px' }}
            >
              PulseChainネットワークのリアルタイム統計情報
            </Typography>
          </motion.div>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        {loading && !stats ? (
          <Box sx={{ width: '100%', textAlign: 'center', py: 8 }}>
            <LinearProgress />
            <Typography variant="h6" sx={{ mt: 2 }}>
              ネットワーク統計を読み込み中...
            </Typography>
          </Box>
        ) : (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
              <Typography variant="body2" color="text.secondary">
                最終更新: {lastUpdated ? lastUpdated.toLocaleString() : '更新中...'}
              </Typography>
              <Button 
                startIcon={<RefreshIcon />} 
                onClick={fetchNetworkStats}
                disabled={loading}
              >
                更新
              </Button>
            </Box>
            
            <Grid container spacing={3}>
              {/* 主要統計カード */}
              <Grid item xs={12} md={3}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)'
                    }
                  }}
                  data-aos="fade-up"
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <StorageIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">ノード</Typography>
                    </Box>
                    <Typography variant="h3" component="div" gutterBottom>
                      {formatNumber(stats.nodes.total)}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        アクティブ: {formatNumber(stats.nodes.active)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        バリデーター: {formatNumber(stats.nodes.validators)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)'
                    }
                  }}
                  data-aos="fade-up"
                  data-aos-delay="100"
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <ReceiptLongIcon color="secondary" sx={{ mr: 1 }} />
                      <Typography variant="h6">トランザクション</Typography>
                    </Box>
                    <Typography variant="h3" component="div" gutterBottom>
                      {formatLargeNumber(stats.transactions.total)}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        24時間: {formatLargeNumber(stats.transactions.daily)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        保留中: {formatNumber(stats.transactions.pending)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)'
                    }
                  }}
                  data-aos="fade-up"
                  data-aos-delay="200"
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SpeedIcon sx={{ color: '#4caf50', mr: 1 }} />
                      <Typography variant="h6">パフォーマンス</Typography>
                    </Box>
                    <Typography variant="h3" component="div" gutterBottom>
                      {stats.performance.currentTps} TPS
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        ピーク: {stats.performance.peakTps} TPS
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        ブロック時間: {stats.blocks.avgTime}秒
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)'
                    }
                  }}
                  data-aos="fade-up"
                  data-aos-delay="300"
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AccountBalanceWalletIcon sx={{ color: '#ff9800', mr: 1 }} />
                      <Typography variant="h6">ステーキング</Typography>
                    </Box>
                    <Typography variant="h3" component="div" gutterBottom>
                      {formatLargeNumber(stats.network.totalStaked)}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        バリデーター: {formatNumber(stats.network.activeValidators)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        最新ブロック: {formatNumber(stats.blocks.latest)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* チャートセクション */}
              <Grid item xs={12} md={8}>
                <Paper 
                  elevation={2} 
                  sx={{ p: 3, height: '100%' }}
                  data-aos="fade-up"
                  data-aos-delay="400"
                >
                  <Typography variant="h6" gutterBottom>
                    過去24時間のTPS (トランザクション/秒)
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <Line data={tpsChartData} options={chartOptions} />
                  </Box>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper 
                  elevation={2} 
                  sx={{ p: 3, height: '100%' }}
                  data-aos="fade-up"
                  data-aos-delay="500"
                >
                  <Typography variant="h6" gutterBottom>
                    ノード地域分布
                  </Typography>
                  <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Doughnut data={regionChartData} options={doughnutOptions} />
                  </Box>
                </Paper>
              </Grid>
              
              <Grid item xs={12}>
                <Paper 
                  elevation={2} 
                  sx={{ p: 3 }}
                  data-aos="fade-up"
                  data-aos-delay="600"
                >
                  <Typography variant="h6" gutterBottom>
                    過去7日間のトランザクション数
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <Line data={txChartData} options={chartOptions} />
                  </Box>
                </Paper>
              </Grid>
              
              {/* トップバリデーターテーブル */}
              <Grid item xs={12}>
                <Paper 
                  elevation={2} 
                  sx={{ p: 3, mt: 2 }}
                  data-aos="fade-up"
                  data-aos-delay="700"
                >
                  <Typography variant="h6" gutterBottom>
                    トップバリデーター
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>バリデーター名</TableCell>
                          <TableCell>国</TableCell>
                          <TableCell align="right">ノード数</TableCell>
                          <TableCell align="right">稼働率</TableCell>
                          <TableCell align="right">ステーキング量</TableCell>
                          <TableCell align="right">シェア</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.topValidators.map((validator: any, index: number) => (
                          <TableRow 
                            key={index}
                            sx={{ 
                              '&:hover': { 
                                bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)' 
                              }
                            }}
                          >
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <VerifiedUserIcon 
                                  sx={{ 
                                    mr: 1, 
                                    color: index < 3 ? theme.palette.primary.main : 'inherit',
                                    fontSize: '1.2rem'
                                  }} 
                                />
                                {validator.name}
                                {index < 3 && (
                                  <Chip 
                                    label={`Top ${index + 1}`} 
                                    size="small" 
                                    color="primary" 
                                    variant="outlined"
                                    sx={{ ml: 1, height: 20 }}
                                  />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <span style={{ marginRight: '8px', fontSize: '1.2rem' }}>
                                  {countryFlags[validator.country] || '🌐'}
                                </span>
                                {validator.country}
                              </Box>
                            </TableCell>
                            <TableCell align="right">{validator.nodes}</TableCell>
                            <TableCell align="right">
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                                {validator.uptime}%
                                <Box 
                                  sx={{ 
                                    width: 40, 
                                    ml: 1, 
                                    height: 4, 
                                    borderRadius: 2,
                                    bgcolor: 
                                      validator.uptime > 99.9 ? '#4caf50' : 
                                      validator.uptime > 99.5 ? '#8bc34a' : 
                                      validator.uptime > 99.0 ? '#ffc107' : 
                                      '#f44336'
                                  }} 
                                />
                              </Box>
                            </TableCell>
                            <TableCell align="right">{formatLargeNumber(validator.staked)}</TableCell>
                            <TableCell align="right">
                              {(validator.staked / stats.network.totalStaked * 100).toFixed(2)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 6, textAlign: 'center' }}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                <Typography variant="h5" gutterBottom>
                  PulseChainネットワークの一員になりませんか？
                </Typography>
                <Typography variant="body1" paragraph sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
                  バリデーターとして参加することで、ネットワークの安全性向上に貢献し、報酬を得ることができます。
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  size="large"
                  component={RouterLink}
                  to="/become-validator"
                  sx={{ 
                    fontWeight: 'bold',
                    px: 4,
                    py: 1.5,
                    borderRadius: 8,
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 10px 20px rgba(0,0,0,0.2)'
                    }
                  }}
                >
                  バリデーターになる
                </Button>
              </motion.div>
            </Box>
          </>
        )}
      </Container>
    </Box>
  );
};

export default NetworkStats;