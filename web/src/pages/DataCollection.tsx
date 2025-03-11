import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Divider,
  useTheme
} from '@mui/material';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import CurrencyBitcoinIcon from '@mui/icons-material/CurrencyBitcoin';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import DevicesIcon from '@mui/icons-material/Devices';
import PublicIcon from '@mui/icons-material/Public';
import BatteryChargingFullIcon from '@mui/icons-material/BatteryChargingFull';
import DataSourceCard from '../components/DataSourceCard';
import CodeBlock from '../components/CodeBlock';

const DataCollection = () => {
  const theme = useTheme();
  
  const weatherApiSample = `{
  "temperature": 25.5,
  "humidity": 60.0,
  "pressure": 1013.2,
  "wind_speed": 5.2,
  "location": "Tokyo",
  "timestamp": 1678912345
}`;

  const bitcoinDataSample = `{
  "latest_block_hash": "000000000000000000025c39908f7f27a2d1b8c5a7c9c4f9e8d7c6b5a4d3c2b1",
  "block_height": 780123,
  "timestamp": 1678912400,
  "difficulty": 35364065900.72
}`;

  const stockMarketSample = `{
  "market_index": 29123.45,
  "volatility": 1.23,
  "trading_volume": 5234567890,
  "timestamp": 1678912500
}`;

  const earthquakeDataSample = `{
  "earthquake_count": 5,
  "max_magnitude": 3.2,
  "locations": ["Pacific Ring", "Japan", "California"],
  "timestamp": 1678912600
}`;

  const browserDataSample = `{
  "battery_level": 78.5,
  "network_type": "wifi",
  "connection_speed": 25.4,
  "device_orientation": {
    "alpha": 120.5,
    "beta": 45.2,
    "gamma": -10.1
  },
  "ambient_light": 450.2,
  "timestamp": 1678912700
}`;

  const combinedDataCode = `// 環境データの収集と組み合わせ
const collectEnvironmentalData = async () => {
  // 各データソースからデータを収集
  const weatherData = await fetchWeatherData();
  const bitcoinData = await fetchBitcoinData();
  const stockMarketData = await fetchStockMarketData();
  const earthquakeData = await fetchEarthquakeData();
  const browserData = await collectBrowserData();
  
  // データを組み合わせて環境データを作成
  const combinedData = {
    temperature: weatherData.temperature,
    humidity: weatherData.humidity,
    pressure: weatherData.pressure,
    bitcoin_hash: bitcoinData.latest_block_hash.substring(0, 16),
    market_volatility: stockMarketData.volatility,
    earthquake_activity: earthquakeData.earthquake_count > 0,
    device_motion: {
      x: browserData.device_orientation.beta,
      y: browserData.device_orientation.gamma,
      z: browserData.device_orientation.alpha
    },
    battery_level: browserData.battery_level,
    timestamp: Date.now() / 1000
  };
  
  return combinedData;
};`;

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
            環境データ収集
          </Typography>
          <Typography variant="h6" sx={{ maxWidth: '800px' }}>
            PulseChainは多様なデータソースから環境データを収集し、予測不可能で検証可能なランダム性を生成します。
          </Typography>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
          データソース
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 4 }}>
          PulseChainは以下のような多様なデータソースから環境データを収集します。これらのデータは公開され検証可能なため、
          誰でも同じデータにアクセスして検証することができます。
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="気象データ"
              description="Open-MeteoやOpenWeatherMapなどの公開APIから取得する気象データ。温度、湿度、気圧、風速などの情報を含みます。"
              icon={<WbSunnyIcon fontSize="inherit" />}
              sampleData={weatherApiSample}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="ビットコインブロックチェーン"
              description="ビットコインの最新ブロックハッシュやネットワーク状態を環境エントロピーとして利用します。約10分ごとに更新される予測不可能な値です。"
              icon={<CurrencyBitcoinIcon fontSize="inherit" />}
              sampleData={bitcoinDataSample}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="株式市場データ"
              description="株式市場の指数、ボラティリティ、取引量などのデータを利用します。市場の自然な変動を環境データとして活用します。"
              icon={<ShowChartIcon fontSize="inherit" />}
              sampleData={stockMarketSample}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="地震データ"
              description="USGS APIなどから取得する世界中の地震活動データ。地震の数、マグニチュード、発生場所などを数値化します。"
              icon={<PublicIcon fontSize="inherit" />}
              sampleData={earthquakeDataSample}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="ブラウザ/デバイスデータ"
              description="ユーザーのブラウザから収集するデータ。バッテリーレベル、ネットワーク情報、デバイスの向き、環境光センサーなどの情報を含みます。"
              icon={<DevicesIcon fontSize="inherit" />}
              sampleData={browserDataSample}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={4}>
            <DataSourceCard
              title="ゼロエネルギーセンサー"
              description="将来的には、太陽光、振動、風力などから電力を得る低電力センサーからのデータも活用します。環境に優しい持続可能なデータソースです。"
              icon={<BatteryChargingFullIcon fontSize="inherit" />}
            />
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 6 }} />
        
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
          データの組み合わせと処理
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} lg={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                データの組み合わせ
              </Typography>
              <Typography variant="body2" paragraph>
                収集した多様なデータソースを組み合わせて、一意の環境データを生成します。
                これにより、単一のデータソースの操作による攻撃を防止し、より高い予測不可能性を実現します。
              </Typography>
              <CodeBlock code={combinedDataCode} language="javascript" />
            </Paper>
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                データの処理フロー
              </Typography>
              <Typography variant="body2" paragraph>
                環境データの収集から処理までの流れ:
              </Typography>
              <Box component="ol" sx={{ pl: 2 }}>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>データ収集:</strong> 複数のソースから環境データを収集
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>データ正規化:</strong> 異なるソースからのデータを統一形式に変換
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>データ組み合わせ:</strong> 複数のデータソースを一つの環境データに統合
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>ハッシュ化:</strong> 環境データをSHA-256などのハッシュ関数で一意のハッシュ値に変換
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>VRF処理:</strong> ハッシュ値をVRF（検証可能なランダム関数）で処理し、ランダム値と証明を生成
                  </Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body2">
                    <strong>リーダー選出:</strong> 生成されたランダム値に基づいてリーダーノードを選出
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 6 }}>
          <Paper elevation={3} sx={{ p: 3, borderLeft: `4px solid ${theme.palette.primary.main}` }}>
            <Typography variant="h6" gutterBottom>
              なぜ環境データなのか？
            </Typography>
            <Typography variant="body2">
              環境データを使用する主な利点:
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body2">
                  <strong>予測不可能性:</strong> 自然現象や分散型システムの予測不可能な変動を利用
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body2">
                  <strong>透明性:</strong> すべてのデータが公開され検証可能
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body2">
                  <strong>分散性:</strong> 地理的に分散したデータソースにより、局所的な操作を防止
                </Typography>
              </Box>
              <Box component="li">
                <Typography variant="body2">
                  <strong>持続可能性:</strong> 環境データの収集は低エネルギーで実現可能
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
};

export default DataCollection;