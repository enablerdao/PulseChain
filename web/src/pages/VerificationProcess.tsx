import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  useTheme
} from '@mui/material';
import CodeBlock from '../components/CodeBlock';
import DataFlowDiagram from '../components/DataFlowDiagram';

const VerificationProcess = () => {
  const theme = useTheme();
  
  const verificationSteps = [
    {
      label: 'データソースの検証',
      description: '各データソースは公開APIを通じて誰でも取得可能。タイムスタンプと位置情報に基づいて同じデータを再取得して検証します。',
      code: `// 気象データの検証
const verifyWeatherData = async (claimedData, timestamp, location) => {
  // 同じタイムスタンプと位置情報で公開APIから直接データを取得
  const actualData = await fetchFromOpenMeteoApi(timestamp, location);
  
  // データの一致を確認
  return isDataMatching(claimedData, actualData);
};`
    },
    {
      label: 'ハッシュの検証',
      description: '環境データから同じハッシュ値が生成されることを確認します。',
      code: `// 環境データのハッシュ検証
const verifyEnvironmentalHash = (environmentalData, claimedHash) => {
  // 環境データを同じ方法でハッシュ化
  const calculatedHash = hashEnvironmentalData(environmentalData);
  
  // ハッシュ値の一致を確認
  return calculatedHash === claimedHash;
};`
    },
    {
      label: 'VRF出力の検証',
      description: '公開鍵、環境ハッシュ、証明を使用してランダム値を検証します。',
      code: `// VRF出力の検証
const verifyVrfOutput = (randomValue, proof, envHash, publicKey) => {
  // VRFの検証関数を使用
  return vrf.verify(randomValue, proof, envHash, publicKey);
};`
    },
    {
      label: 'リーダー選出の検証',
      description: '検証されたランダム値から、同じリーダー選出ロジックを実行し、結果が一致することを確認します。',
      code: `// リーダー選出の検証
const verifyLeaderSelection = (randomValue, nodeList, claimedLeader) => {
  // ランダム値からリーダーを決定するロジックを再実行
  const expectedLeader = determineLeader(randomValue, nodeList);
  
  // 主張されたリーダーが正しいか確認
  return expectedLeader === claimedLeader;
};`
    }
  ];

  const dataFlowSteps = [
    {
      title: '環境データ',
      description: '公開データソースから収集',
      color: theme.palette.primary.main
    },
    {
      title: 'ハッシュ値',
      description: 'SHA-256でハッシュ化',
      color: theme.palette.secondary.main
    },
    {
      title: 'VRF処理',
      description: 'ランダム値と証明を生成',
      color: '#2e7d32' // green
    },
    {
      title: '検証',
      description: '全ノードが結果を検証',
      color: '#d32f2f' // red
    }
  ];

  const fullVerificationCode = `// 完全な検証プロセス
const verifyConsensusProcess = async (
  environmentalData,
  claimedHash,
  randomValue,
  proof,
  publicKey,
  claimedLeader,
  nodeList
) => {
  // ステップ1: データソースの検証
  const isDataValid = await verifyDataSources(environmentalData);
  if (!isDataValid) return false;
  
  // ステップ2: ハッシュの検証
  const isHashValid = verifyEnvironmentalHash(environmentalData, claimedHash);
  if (!isHashValid) return false;
  
  // ステップ3: VRF出力の検証
  const isVrfValid = verifyVrfOutput(randomValue, proof, claimedHash, publicKey);
  if (!isVrfValid) return false;
  
  // ステップ4: リーダー選出の検証
  const isLeaderValid = verifyLeaderSelection(randomValue, nodeList, claimedLeader);
  if (!isLeaderValid) return false;
  
  // すべての検証が成功
  return true;
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
            検証プロセス
          </Typography>
          <Typography variant="h6" sx={{ maxWidth: '800px' }}>
            PulseChainの環境同期型コンセンサスは、透明性と検証可能性を重視しています。
            すべてのステップが公開され、誰でも検証できます。
          </Typography>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
          検証フロー
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 4 }}>
          PulseChainの環境同期型コンセンサスは、以下のステップで検証されます。
          各ステップは公開され検証可能であり、ネットワーク参加者は同じプロセスを実行して結果を確認できます。
        </Typography>
        
        <DataFlowDiagram steps={dataFlowSteps} />
        
        <Box sx={{ mt: 6 }}>
          <Stepper orientation="vertical">
            {verificationSteps.map((step, index) => (
              <Step key={index} active={true}>
                <StepLabel>
                  <Typography variant="h6">{step.label}</Typography>
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" paragraph>
                    {step.description}
                  </Typography>
                  <Paper elevation={0} sx={{ bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.50', p: 2, mb: 2 }}>
                    <CodeBlock code={step.code} language="javascript" />
                  </Paper>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Box>
        
        <Divider sx={{ my: 6 }} />
        
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
          完全な検証プロセス
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} lg={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                検証コード
              </Typography>
              <Typography variant="body2" paragraph>
                以下は、環境同期型コンセンサスの完全な検証プロセスを示すコードです。
                各ステップを順番に実行し、すべてのステップが成功した場合にのみ検証が成功します。
              </Typography>
              <CodeBlock code={fullVerificationCode} language="javascript" />
            </Paper>
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                セキュリティと信頼性
              </Typography>
              <Typography variant="body2" paragraph>
                PulseChainの検証プロセスは、以下の特性によって高いセキュリティと信頼性を実現しています:
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>操作耐性:</strong> 複数の独立したデータソースを使用することで、単一のソースの操作による攻撃を防止します。
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>予測不可能性:</strong> 自然現象や分散型システムの予測不可能な変動を利用し、将来のリーダー選出を予測することを困難にします。
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>透明性:</strong> すべてのデータと処理が公開され検証可能であり、誰でも同じ結果を再現できます。
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>分散性:</strong> 地理的に分散したデータソースにより、局所的な操作を防止します。
                  </Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body2">
                    <strong>効率性:</strong> 検証プロセスは計算効率が高く、低リソースでも実行可能です。
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 6 }}>
          <Paper elevation={3} sx={{ p: 3, borderLeft: `4px solid ${theme.palette.secondary.main}` }}>
            <Typography variant="h6" gutterBottom>
              検証の重要性
            </Typography>
            <Typography variant="body2" paragraph>
              分散型システムにおいて、検証可能性は信頼の基盤です。PulseChainの環境同期型コンセンサスは、
              すべてのステップが公開され検証可能であることを保証し、参加者が互いを信頼する必要なく
              システム全体を信頼できるようにしています。
            </Typography>
            <Typography variant="body2">
              この透明性と検証可能性により、PulseChainは真の分散型システムとしての信頼性を確立し、
              中央集権的な権威に依存することなく、公平で安全なコンセンサスを実現します。
            </Typography>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
};

export default VerificationProcess;