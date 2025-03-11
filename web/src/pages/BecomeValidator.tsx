import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  TextField,
  Alert,
  Divider,
  Card,
  CardContent,
  CardMedia,
  useTheme
} from '@mui/material';
import { useState } from 'react';
import { motion } from 'framer-motion';
import CodeBlock from '../components/CodeBlock';

const BecomeValidator = () => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [email, setEmail] = useState('');
  const [nodeId, setNodeId] = useState('');
  const [submitted, setSubmitted] = useState(false);
  
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    // 実際のアプリケーションではここでAPIリクエストを送信
  };

  const generateNodeId = () => {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 16; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    setNodeId(result);
  };

  const validatorSteps = [
    {
      label: 'ハードウェア要件の確認',
      description: 'PulseChainのバリデーターノードを実行するには、以下の最小要件を満たすハードウェアが必要です。',
      content: (
        <Box>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>最小要件</Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>CPU:</strong> 4コア以上
                    </Typography>
                  </Box>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>RAM:</strong> 8GB以上
                    </Typography>
                  </Box>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>ストレージ:</strong> 100GB SSD以上
                    </Typography>
                  </Box>
                  <Box component="li">
                    <Typography variant="body2">
                      <strong>インターネット:</strong> 10Mbps以上の安定した接続
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>推奨要件</Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>CPU:</strong> 8コア以上
                    </Typography>
                  </Box>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>RAM:</strong> 16GB以上
                    </Typography>
                  </Box>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>ストレージ:</strong> 500GB SSD以上
                    </Typography>
                  </Box>
                  <Box component="li">
                    <Typography variant="body2">
                      <strong>インターネット:</strong> 25Mbps以上の安定した接続
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
          <Alert severity="info" sx={{ mt: 3 }}>
            PulseChainのゼロエネルギー設計により、一般的なブロックチェーンよりも低いハードウェア要件で運用できます。
            また、太陽光パネルなどの再生可能エネルギー源を使用することで、運用コストをさらに削減できます。
          </Alert>
        </Box>
      )
    },
    {
      label: 'ソフトウェアのインストール',
      description: 'PulseChainのバリデーターソフトウェアをインストールします。',
      content: (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            以下のコマンドを実行して、PulseChainのバリデーターソフトウェアをインストールします。
          </Typography>
          
          <CodeBlock 
            code={`# リポジトリのクローン
git clone https://github.com/enablerdao/PulseChain.git
cd PulseChain

# 依存関係のインストール
pip install -r requirements.txt

# バリデーターノードの初期化
python validator_setup.py --init`} 
            language="bash" 
          />
          
          <Alert severity="success" sx={{ mt: 3 }}>
            インストールが完了すると、バリデーターノードの初期設定ファイルが生成されます。
          </Alert>
        </Box>
      )
    },
    {
      label: 'ノードの設定',
      description: 'バリデーターノードの基本設定を行います。',
      content: (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            生成された設定ファイル（config.yaml）を編集して、ノードの基本設定を行います。
          </Typography>
          
          <CodeBlock 
            code={`# config.yaml
node:
  name: "MyPulseChainNode"  # ノードの名前（任意）
  network: "mainnet"        # mainnet または testnet
  port: 52964               # ネットワークポート
  
validator:
  enabled: true             # バリデーターモードを有効化
  stake_amount: 1000        # ステーキング量（最小1000）
  
environmental_data:
  sources:
    - weather_api: true     # 気象データの使用
    - bitcoin_data: true    # ビットコインデータの使用
    - browser_data: true    # ブラウザデータの使用
    
zero_energy:
  enabled: true             # ゼロエネルギーモードを有効化
  target_cpu_usage: 30.0    # 目標CPU使用率（%）`} 
            language="yaml" 
          />
          
          <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>
            設定が完了したら、以下のコマンドでノードIDを生成します。
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, mb: 3 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={generateNodeId}
              sx={{ mr: 2 }}
            >
              ノードID生成
            </Button>
            
            {nodeId && (
              <TextField
                label="あなたのノードID"
                value={nodeId}
                variant="outlined"
                fullWidth
                InputProps={{
                  readOnly: true,
                }}
              />
            )}
          </Box>
          
          <Alert severity="warning">
            生成されたノードIDは安全に保管してください。このIDはネットワーク上であなたのノードを識別するために使用されます。
          </Alert>
        </Box>
      )
    },
    {
      label: 'バリデーターの登録',
      description: 'PulseChainネットワークにバリデーターとして登録します。',
      content: (
        <Box component="form" onSubmit={handleSubmit}>
          <Typography variant="subtitle1" gutterBottom>
            以下の情報を入力して、PulseChainネットワークにバリデーターとして登録します。
          </Typography>
          
          <TextField
            label="メールアドレス"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            required
            margin="normal"
          />
          
          <TextField
            label="ノードID"
            value={nodeId}
            onChange={(e) => setNodeId(e.target.value)}
            fullWidth
            required
            margin="normal"
          />
          
          {submitted ? (
            <Alert severity="success" sx={{ mt: 3 }}>
              登録が完了しました！確認メールを送信しました。メールに記載されている手順に従って、バリデーターの設定を完了してください。
            </Alert>
          ) : (
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              fullWidth 
              sx={{ mt: 3 }}
            >
              バリデーターとして登録
            </Button>
          )}
        </Box>
      )
    },
    {
      label: 'ノードの起動',
      description: 'バリデーターノードを起動して、ネットワークに参加します。',
      content: (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            以下のコマンドを実行して、バリデーターノードを起動します。
          </Typography>
          
          <CodeBlock 
            code={`# バリデーターノードの起動
python advanced_pulsechain.py --validator --node-id YOUR_NODE_ID

# バックグラウンドで実行する場合
nohup python advanced_pulsechain.py --validator --node-id YOUR_NODE_ID > validator.log 2>&1 &`} 
            language="bash" 
          />
          
          <Alert severity="info" sx={{ mt: 3 }}>
            ノードが起動すると、自動的にネットワークに接続し、環境データの収集と検証を開始します。
            初期同期には数時間かかる場合があります。
          </Alert>
          
          <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>
            以下のコマンドでノードのステータスを確認できます。
          </Typography>
          
          <CodeBlock 
            code={`# ノードのステータス確認
python node_status.py

# 出力例:
# ノードID: abcd1234efgh5678
# ステータス: アクティブ
# 同期状態: 100%
# 検証済みトランザクション: 1,234
# 信頼スコア: 98.5
# 報酬: 123.45 PULSE`} 
            language="bash" 
          />
        </Box>
      )
    }
  ];

  const benefitItems = [
    {
      title: "報酬の獲得",
      description: "バリデーターとして参加することで、トランザクション検証の報酬としてPULSEトークンを獲得できます。",
      icon: "💰",
      color: "#FFD700"
    },
    {
      title: "低エネルギー消費",
      description: "PulseChainのゼロエネルギー設計により、従来のブロックチェーンよりも大幅に低い電力消費で運用できます。",
      icon: "🌱",
      color: "#4CAF50"
    },
    {
      title: "分散型ガバナンス",
      description: "バリデーターはネットワークの意思決定に参加でき、プロトコルの進化に影響を与えることができます。",
      icon: "🗳️",
      color: "#2196F3"
    },
    {
      title: "信頼スコアの構築",
      description: "長期間安定して運用することで信頼スコアが向上し、より多くの報酬を獲得できるようになります。",
      icon: "⭐",
      color: "#FF9800"
    }
  ];

  return (
    <Box>
      {/* ヘッダーセクション */}
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
              バリデーターになる
            </Typography>
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              sx={{ mb: 4, maxWidth: '800px' }}
            >
              PulseChainネットワークのバリデーターになって、環境同期型コンセンサスに参加しましょう。
              わずか5ステップで簡単に始められます。
            </Typography>
          </motion.div>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Grid container spacing={6}>
          <Grid item xs={12} md={8}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Typography variant="h4" component="h2" gutterBottom>
                バリデーターになるステップ
              </Typography>
              <Typography variant="body1" paragraph sx={{ mb: 4 }}>
                PulseChainのバリデーターになるプロセスは非常にシンプルです。
                以下のステップに従って、環境同期型コンセンサスネットワークに参加しましょう。
              </Typography>
              
              <Stepper activeStep={activeStep} orientation="vertical" sx={{ mb: 4 }}>
                {validatorSteps.map((step, index) => (
                  <Step key={index}>
                    <StepLabel>
                      <Typography variant="h6">{step.label}</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" paragraph>
                        {step.description}
                      </Typography>
                      {step.content}
                      <Box sx={{ mt: 3, mb: 2 }}>
                        <Button
                          variant="contained"
                          onClick={handleNext}
                          sx={{ mr: 1 }}
                          disabled={index === validatorSteps.length - 1}
                        >
                          {index === validatorSteps.length - 1 ? '完了' : '次へ'}
                        </Button>
                        <Button
                          disabled={index === 0}
                          onClick={handleBack}
                          sx={{ mr: 1 }}
                        >
                          戻る
                        </Button>
                      </Box>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </motion.div>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
                <Typography variant="h5" gutterBottom>
                  バリデーターの特典
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                {benefitItems.map((item, index) => (
                  <Box key={index} sx={{ mb: 2, display: 'flex', alignItems: 'flex-start' }}>
                    <Box 
                      sx={{ 
                        mr: 2, 
                        fontSize: '2rem',
                        backgroundColor: item.color,
                        width: 50,
                        height: 50,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '50%',
                        flexShrink: 0
                      }}
                    >
                      {item.icon}
                    </Box>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {item.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.description}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Paper>
              
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  サポート
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" paragraph>
                  バリデーターの設定や運用に関するご質問は、以下のサポートチャンネルをご利用ください。
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>Discord:</strong> PulseChain Validators
                    </Typography>
                  </Box>
                  <Box component="li" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>Telegram:</strong> @PulseChainValidators
                    </Typography>
                  </Box>
                  <Box component="li">
                    <Typography variant="body2">
                      <strong>メール:</strong> validators@pulsechain.example.com
                    </Typography>
                  </Box>
                </Box>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  fullWidth 
                  sx={{ mt: 2 }}
                >
                  ドキュメントを見る
                </Button>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 6 }} />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
            バリデーターの成功事例
          </Typography>
          
          <Grid container spacing={4}>
            {[
              {
                name: "田中 太郎",
                location: "東京",
                image: "https://randomuser.me/api/portraits/men/32.jpg",
                quote: "PulseChainのバリデーターになって3ヶ月。自宅のPCで運用していますが、電気代はほとんど変わらず、毎月安定した報酬を得ています。",
                stats: { nodes: 1, rewards: "約15,000 PULSE/月", uptime: "99.8%" }
              },
              {
                name: "鈴木 花子",
                location: "大阪",
                image: "https://randomuser.me/api/portraits/women/44.jpg",
                quote: "太陽光パネルと組み合わせて運用しています。環境に優しいブロックチェーンに貢献できることが嬉しいです。セットアップも簡単でした。",
                stats: { nodes: 3, rewards: "約42,000 PULSE/月", uptime: "99.9%" }
              },
              {
                name: "佐藤 健",
                location: "福岡",
                image: "https://randomuser.me/api/portraits/men/67.jpg",
                quote: "他のブロックチェーンのバリデーターもやっていますが、PulseChainは断然省エネで、設定も簡単です。コミュニティのサポートも素晴らしい。",
                stats: { nodes: 5, rewards: "約75,000 PULSE/月", uptime: "99.7%" }
              }
            ].map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardMedia
                    component="img"
                    height="200"
                    image={testimonial.image}
                    alt={testimonial.name}
                    sx={{ objectFit: 'cover' }}
                  />
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h5" component="div">
                      {testimonial.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {testimonial.location}
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ mt: 2, fontStyle: 'italic' }}>
                      "{testimonial.quote}"
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          ノード数
                        </Typography>
                        <Typography variant="h6">
                          {testimonial.stats.nodes}
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          稼働率
                        </Typography>
                        <Typography variant="h6">
                          {testimonial.stats.uptime}
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          報酬
                        </Typography>
                        <Typography variant="h6" sx={{ fontSize: '0.9rem' }}>
                          {testimonial.stats.rewards}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </motion.div>
        
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Typography variant="h4" gutterBottom>
              今すぐバリデーターになりましょう
            </Typography>
            <Typography variant="body1" paragraph sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
              PulseChainのバリデーターになって、革新的な環境同期型コンセンサスに参加しましょう。
              低エネルギー消費で高い報酬を得るチャンスです。
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              size="large"
              onClick={() => setActiveStep(0)}
              sx={{ 
                fontWeight: 'bold',
                px: 4,
                py: 1.5,
                borderRadius: 8
              }}
            >
              今すぐ始める
            </Button>
          </motion.div>
        </Box>
      </Container>
    </Box>
  );
};

export default BecomeValidator;