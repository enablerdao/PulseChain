import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  useTheme
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import DataFlowDiagram from '../components/DataFlowDiagram';

const Home = () => {
  const theme = useTheme();
  
  const dataFlowSteps = [
    {
      title: '環境データ収集',
      description: '多様なソースからデータを収集',
      color: theme.palette.primary.main
    },
    {
      title: 'ハッシュ化',
      description: 'データを一意のハッシュに変換',
      color: theme.palette.secondary.main
    },
    {
      title: 'VRF処理',
      description: '検証可能なランダム値を生成',
      color: '#2e7d32' // green
    },
    {
      title: 'リーダー選出',
      description: 'ランダム値に基づく公平な選出',
      color: '#d32f2f' // red
    }
  ];

  return (
    <Box>
      {/* ヒーローセクション */}
      <Box 
        sx={{ 
          bgcolor: 'primary.main', 
          color: 'white',
          py: 8,
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
        <Container maxWidth="md">
          <Typography 
            variant="h2" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontWeight: 'bold',
              textShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
          >
            PulseChain 環境同期型コンセンサス
          </Typography>
          <Typography 
            variant="h5" 
            component="h2" 
            gutterBottom
            sx={{ mb: 4, maxWidth: '800px' }}
          >
            自然環境と分散型データソースを活用した革新的なブロックチェーン技術
          </Typography>
          <Box sx={{ mt: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button 
              variant="contained" 
              color="secondary" 
              size="large"
              component={RouterLink}
              to="/data-collection"
              sx={{ 
                color: 'white',
                fontWeight: 'bold',
                px: 4,
                py: 1.5,
                borderRadius: 8
              }}
            >
              データ収集の詳細
            </Button>
            <Button 
              variant="outlined" 
              color="inherit" 
              size="large"
              component={RouterLink}
              to="/verification-process"
              sx={{ 
                borderColor: 'white',
                color: 'white',
                fontWeight: 'bold',
                px: 4,
                py: 1.5,
                borderRadius: 8
              }}
            >
              検証プロセスを見る
            </Button>
          </Box>
        </Container>
      </Box>

      {/* 概要セクション */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography 
          variant="h3" 
          component="h2" 
          gutterBottom
          align="center"
          sx={{ mb: 6, fontWeight: 'bold' }}
        >
          PulseChainの環境同期型コンセンサス
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 4, fontSize: '1.1rem' }}>
          PulseChainは、従来のブロックチェーンの限界を超える革新的なレイヤー1プロトコルです。
          環境同期型コンセンサスメカニズムは、自然環境や分散型データソースから収集したデータを活用し、
          公平で安全なリーダー選出を実現します。
        </Typography>
        
        <DataFlowDiagram steps={dataFlowSteps} />
        
        <Grid container spacing={4} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 140,
                  bgcolor: 'primary.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '3rem'
                }}
              >
                🌍
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  多様なデータソース
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  気象データ、ビットコインブロックチェーン、株式市場、地震データなど、
                  多様な公開データソースから環境データを収集します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 140,
                  bgcolor: 'secondary.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '3rem'
                }}
              >
                🔍
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  検証可能なランダム性
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  VRF（検証可能なランダム関数）を使用して、予測不可能だが検証可能なランダム値を生成し、
                  透明性と公平性を確保します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 140,
                  bgcolor: '#2e7d32', // green
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '3rem'
                }}
              >
                🛡️
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  セキュリティと信頼性
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  複数の独立したデータソースを使用することで、単一のソースの操作による攻撃を防止し、
                  高いセキュリティと信頼性を実現します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* CTAセクション */}
      <Box 
        sx={{ 
          bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100',
          py: 6
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h4" align="center" gutterBottom>
            PulseChainの革新的な技術を体験しよう
          </Typography>
          <Typography variant="body1" align="center" paragraph sx={{ mb: 4 }}>
            環境データの収集から検証プロセスまで、PulseChainの仕組みを詳しく見てみましょう。
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button 
              variant="contained" 
              color="primary" 
              size="large"
              component={RouterLink}
              to="/live-demo"
              sx={{ 
                fontWeight: 'bold',
                px: 4,
                py: 1.5,
                borderRadius: 8
              }}
            >
              ライブデモを試す
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;