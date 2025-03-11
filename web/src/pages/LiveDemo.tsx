import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  useTheme
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import CodeBlock from '../components/CodeBlock';

// ChartJSの登録
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const LiveDemo = () => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  
  // 状態管理
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [environmentalData, setEnvironmentalData] = useState<any>(null);
  const [randomValue, setRandomValue] = useState<string | null>(null);
  const [selectedLeader, setSelectedLeader] = useState<string | null>(null);
  const [dataHistory, setDataHistory] = useState<any[]>([]);
  const [customData, setCustomData] = useState({
    temperature: 25.0,
    humidity: 60.0,
    pressure: 1013.2,
    bitcoin_hash: '000000000000000',
    market_volatility: 1.5,
  });
  
  // シミュレーションデータの生成
  const generateSimulationData = () => {
    setLoading(true);
    setError(null);
    
    setTimeout(() => {
      try {
        // 現在時刻
        const timestamp = Date.now() / 1000;
        
        // 環境データの生成（ランダム要素を含む）
        const data = {
          temperature: customData.temperature + (Math.random() * 2 - 1),
          humidity: customData.humidity + (Math.random() * 5 - 2.5),
          pressure: customData.pressure + (Math.random() * 2 - 1),
          bitcoin_hash: customData.bitcoin_hash,
          market_volatility: customData.market_volatility + (Math.random() * 0.2 - 0.1),
          earthquake_activity: Math.random() > 0.8,
          device_motion: {
            x: Math.random() * 180 - 90,
            y: Math.random() * 180 - 90,
            z: Math.random() * 360
          },
          battery_level: Math.random() * 100,
          timestamp: timestamp
        };
        
        // 環境データの設定
        setEnvironmentalData(data);
        
        // ハッシュ値の生成（実際にはSHA-256などを使用）
        const hash = generateMockHash(data);
        
        // ランダム値の生成（実際にはVRFを使用）
        const randValue = generateMockRandomValue(hash);
        setRandomValue(randValue);
        
        // リーダー選出（ランダム値に基づく）
        const leader = selectLeader(randValue);
        setSelectedLeader(leader);
        
        // 履歴に追加
        setDataHistory(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          temperature: data.temperature,
          humidity: data.humidity,
          pressure: data.pressure,
          randomValue: randValue.substring(0, 8),
          leader: leader
        }].slice(-10)); // 最新10件のみ保持
        
        setLoading(false);
      } catch (err) {
        setError('シミュレーション中にエラーが発生しました');
        setLoading(false);
      }
    }, 1000);
  };
  
  // モックハッシュ生成関数
  const generateMockHash = (data: any) => {
    // 実際のアプリケーションではSHA-256などのハッシュ関数を使用
    const str = JSON.stringify(data);
    let hash = '';
    for (let i = 0; i < 64; i++) {
      hash += '0123456789abcdef'[Math.floor(Math.random() * 16)];
    }
    return hash;
  };
  
  // モックランダム値生成関数
  const generateMockRandomValue = (hash: string) => {
    // 実際のアプリケーションではVRFを使用
    let randValue = '';
    for (let i = 0; i < 32; i++) {
      randValue += '0123456789abcdef'[Math.floor(Math.random() * 16)];
    }
    return randValue;
  };
  
  // リーダー選出関数
  const selectLeader = (randomValue: string) => {
    // ノードリスト（実際のアプリケーションではネットワーク参加者のリスト）
    const nodes = [
      'Node1 (Tokyo)',
      'Node2 (New York)',
      'Node3 (London)',
      'Node4 (Sydney)',
      'Node5 (Singapore)'
    ];
    
    // ランダム値の最初のバイトを数値に変換
    const value = parseInt(randomValue.substring(0, 2), 16);
    
    // ノード数で割った余りをインデックスとして使用
    const index = value % nodes.length;
    
    return nodes[index];
  };
  
  // カスタムデータの更新
  const handleCustomDataChange = (field: string, value: string) => {
    setCustomData(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }));
  };
  
  // チャートデータの準備
  const chartData = {
    labels: dataHistory.map(item => item.timestamp),
    datasets: [
      {
        label: '温度 (°C)',
        data: dataHistory.map(item => item.temperature),
        borderColor: '#f44336',
        backgroundColor: 'rgba(244, 67, 54, 0.5)',
        tension: 0.3,
      },
      {
        label: '湿度 (%)',
        data: dataHistory.map(item => item.humidity),
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.5)',
        tension: 0.3,
      },
      {
        label: '気圧 (hPa)',
        data: dataHistory.map(item => item.pressure),
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.5)',
        tension: 0.3,
        hidden: true, // デフォルトで非表示
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
      title: {
        display: true,
        text: '環境データの推移',
        color: isDarkMode ? '#fff' : '#333'
      },
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
  
  // 自動更新
  useEffect(() => {
    // 初回データ生成
    generateSimulationData();
    
    // 30秒ごとに自動更新
    const interval = setInterval(() => {
      generateSimulationData();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
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
            : 'linear-gradient(135deg, #6e8efb, #a777e3)'
        }}
      >
        <Container maxWidth="lg">
          <Typography 
            variant="h3" 
            component="h1" 
            gutterBottom
            sx={{ fontWeight: 'bold' }}
          >
            ライブデモ
          </Typography>
          <Typography variant="h6" sx={{ maxWidth: '800px' }}>
            PulseChainの環境同期型コンセンサスをリアルタイムでシミュレーションします。
            環境データの収集からリーダー選出までの流れを体験できます。
          </Typography>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                環境データ設定
              </Typography>
              <Typography variant="body2" paragraph>
                シミュレーションに使用する環境データを設定できます。
                値を変更してデータを生成すると、結果が変わります。
              </Typography>
              
              <TextField
                label="温度 (°C)"
                type="number"
                value={customData.temperature}
                onChange={(e) => handleCustomDataChange('temperature', e.target.value)}
                fullWidth
                margin="normal"
                InputProps={{ inputProps: { step: 0.1 } }}
              />
              
              <TextField
                label="湿度 (%)"
                type="number"
                value={customData.humidity}
                onChange={(e) => handleCustomDataChange('humidity', e.target.value)}
                fullWidth
                margin="normal"
                InputProps={{ inputProps: { step: 0.1 } }}
              />
              
              <TextField
                label="気圧 (hPa)"
                type="number"
                value={customData.pressure}
                onChange={(e) => handleCustomDataChange('pressure', e.target.value)}
                fullWidth
                margin="normal"
                InputProps={{ inputProps: { step: 0.1 } }}
              />
              
              <TextField
                label="ビットコインハッシュ (先頭15文字)"
                value={customData.bitcoin_hash}
                onChange={(e) => handleCustomDataChange('bitcoin_hash', e.target.value)}
                fullWidth
                margin="normal"
              />
              
              <TextField
                label="市場ボラティリティ"
                type="number"
                value={customData.market_volatility}
                onChange={(e) => handleCustomDataChange('market_volatility', e.target.value)}
                fullWidth
                margin="normal"
                InputProps={{ inputProps: { step: 0.1 } }}
              />
              
              <Button 
                variant="contained" 
                color="primary" 
                fullWidth 
                sx={{ mt: 2 }}
                onClick={generateSimulationData}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'データを生成'}
              </Button>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                シミュレーション結果
              </Typography>
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      bgcolor: theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.02)'
                    }}
                  >
                    <Typography variant="subtitle2" color="text.secondary">
                      環境データ
                    </Typography>
                    {environmentalData ? (
                      <Box component="pre" sx={{ 
                        mt: 1, 
                        fontSize: '0.75rem',
                        overflow: 'auto',
                        maxHeight: '150px'
                      }}>
                        {JSON.stringify(environmentalData, null, 2)}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        データがありません
                      </Typography>
                    )}
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      bgcolor: theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.02)'
                    }}
                  >
                    <Typography variant="subtitle2" color="text.secondary">
                      生成されたランダム値
                    </Typography>
                    {randomValue ? (
                      <Box sx={{ 
                        mt: 1, 
                        fontSize: '0.75rem',
                        wordBreak: 'break-all'
                      }}>
                        {randomValue}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        データがありません
                      </Typography>
                    )}
                  </Paper>
                </Grid>
                
                <Grid item xs={12}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      bgcolor: theme.palette.primary.main,
                      color: 'white'
                    }}
                  >
                    <Typography variant="subtitle2">
                      選出されたリーダー
                    </Typography>
                    {selectedLeader ? (
                      <Typography variant="h5" sx={{ mt: 1, fontWeight: 'bold' }}>
                        {selectedLeader}
                      </Typography>
                    ) : (
                      <Typography variant="body2">
                        データがありません
                      </Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </Paper>
            
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                データ推移
              </Typography>
              
              {dataHistory.length > 0 ? (
                <Box sx={{ height: 300 }}>
                  <Line data={chartData} options={chartOptions} />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  データがありません
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 6 }}>
          <Typography variant="h5" gutterBottom>
            シミュレーションの説明
          </Typography>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">データ収集プロセス</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                実際のPulseChainでは、多様なデータソースから環境データを収集します。
                このデモでは、入力フォームで設定した値とランダム要素を組み合わせて環境データをシミュレーションしています。
              </Typography>
              <CodeBlock 
                code={`// 環境データの収集（シミュレーション）
const collectEnvironmentalData = () => {
  return {
    temperature: baseTemperature + (Math.random() * 2 - 1),
    humidity: baseHumidity + (Math.random() * 5 - 2.5),
    pressure: basePressure + (Math.random() * 2 - 1),
    bitcoin_hash: bitcoinHash,
    market_volatility: baseVolatility + (Math.random() * 0.2 - 0.1),
    earthquake_activity: Math.random() > 0.8,
    device_motion: {
      x: Math.random() * 180 - 90,
      y: Math.random() * 180 - 90,
      z: Math.random() * 360
    },
    battery_level: Math.random() * 100,
    timestamp: Date.now() / 1000
  };
};`} 
                language="javascript" 
              />
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">ハッシュ化とVRF処理</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                環境データはハッシュ関数（SHA-256など）でハッシュ化され、
                そのハッシュ値がVRF（検証可能なランダム関数）で処理されます。
                このデモでは、簡易的なシミュレーションを行っています。
              </Typography>
              <CodeBlock 
                code={`// 環境データのハッシュ化（実際にはSHA-256などを使用）
const hashEnvironmentalData = (data) => {
  const dataString = JSON.stringify(data);
  return sha256(dataString);
};

// VRF処理（検証可能なランダム関数）
const processWithVRF = (hash, privateKey) => {
  // VRFアルゴリズムを使用してランダム値と証明を生成
  const { randomValue, proof } = vrf.generate(hash, privateKey);
  return { randomValue, proof };
};`} 
                language="javascript" 
              />
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">リーダー選出アルゴリズム</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                生成されたランダム値に基づいて、ネットワーク参加者の中からリーダーを選出します。
                このデモでは、ランダム値の最初のバイトを数値に変換し、ノード数で割った余りをインデックスとして使用しています。
              </Typography>
              <CodeBlock 
                code={`// リーダー選出関数
const selectLeader = (randomValue, nodes) => {
  // ランダム値の最初のバイトを数値に変換
  const value = parseInt(randomValue.substring(0, 2), 16);
  
  // ノード数で割った余りをインデックスとして使用
  const index = value % nodes.length;
  
  return nodes[index];
};`} 
                language="javascript" 
              />
            </AccordionDetails>
          </Accordion>
        </Box>
      </Container>
    </Box>
  );
};

export default LiveDemo;