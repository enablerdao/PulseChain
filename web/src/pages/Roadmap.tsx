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
  useTheme,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  LinearProgress,
  Chip,
  Button
} from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CodeIcon from '@mui/icons-material/Code';
import GroupsIcon from '@mui/icons-material/Groups';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import StorageIcon from '@mui/icons-material/Storage';
import SecurityIcon from '@mui/icons-material/Security';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import SpeedIcon from '@mui/icons-material/Speed';
import PublicIcon from '@mui/icons-material/Public';

const Roadmap = () => {
  const theme = useTheme();
  
  // ロードマップのフェーズ
  const phases = [
    {
      title: "フェーズ1: 研究開発と基盤構築",
      description: "PulseChainの基本的な技術研究と開発基盤の構築",
      timeframe: "2023年Q1 - 2023年Q4",
      status: "完了",
      progress: 100,
      color: theme.palette.success.main,
      icon: <CodeIcon />,
      milestones: [
        {
          title: "コンセプト設計",
          description: "環境同期型コンセンサスメカニズムの理論的設計と検証",
          status: "完了",
          date: "2023年Q1"
        },
        {
          title: "プロトタイプ開発",
          description: "基本的なプロトコルのプロトタイプ実装",
          status: "完了",
          date: "2023年Q2"
        },
        {
          title: "環境データソース統合",
          description: "多様な環境データソースとの統合インターフェース開発",
          status: "完了",
          date: "2023年Q3"
        },
        {
          title: "VRF実装",
          description: "検証可能なランダム関数（VRF）の実装と最適化",
          status: "完了",
          date: "2023年Q4"
        }
      ]
    },
    {
      title: "フェーズ2: テストネットとコミュニティ構築",
      description: "テストネットの立ち上げとコミュニティの形成",
      timeframe: "2024年Q1 - 2024年Q2",
      status: "進行中",
      progress: 65,
      color: theme.palette.primary.main,
      icon: <GroupsIcon />,
      milestones: [
        {
          title: "アルファテストネット",
          description: "開発者向けの初期テストネット公開",
          status: "完了",
          date: "2024年Q1"
        },
        {
          title: "開発者ドキュメント",
          description: "開発者向けの包括的なドキュメント整備",
          status: "完了",
          date: "2024年Q1"
        },
        {
          title: "パブリックテストネット",
          description: "一般ユーザー向けテストネットの公開",
          status: "進行中",
          date: "2024年Q2"
        },
        {
          title: "バグバウンティプログラム",
          description: "セキュリティ強化のためのバグ報奨金プログラム開始",
          status: "進行中",
          date: "2024年Q2"
        }
      ]
    },
    {
      title: "フェーズ3: メインネット準備",
      description: "メインネット立ち上げに向けた最終準備",
      timeframe: "2024年Q3 - 2024年Q4",
      status: "予定",
      progress: 10,
      color: theme.palette.info.main,
      icon: <SettingsSuggestIcon />,
      milestones: [
        {
          title: "セキュリティ監査",
          description: "外部セキュリティ企業による包括的な監査",
          status: "予定",
          date: "2024年Q3"
        },
        {
          title: "パフォーマンス最適化",
          description: "ネットワークのスケーラビリティとパフォーマンスの最終調整",
          status: "予定",
          date: "2024年Q3"
        },
        {
          title: "バリデーター募集",
          description: "初期バリデーターノードの募集と選定",
          status: "予定",
          date: "2024年Q4"
        },
        {
          title: "ジェネシスブロック準備",
          description: "メインネットのジェネシスブロック設定と最終テスト",
          status: "予定",
          date: "2024年Q4"
        }
      ]
    },
    {
      title: "フェーズ4: メインネット立ち上げ",
      description: "PulseChainメインネットの公式立ち上げ",
      timeframe: "2025年Q1",
      status: "予定",
      progress: 0,
      color: theme.palette.warning.main,
      icon: <RocketLaunchIcon />,
      milestones: [
        {
          title: "ジェネシスイベント",
          description: "メインネットの公式立ち上げイベント",
          status: "予定",
          date: "2025年Q1"
        },
        {
          title: "初期エコシステム",
          description: "コアDAppsとサービスの展開",
          status: "予定",
          date: "2025年Q1"
        },
        {
          title: "取引所上場",
          description: "主要取引所へのPULSEトークン上場",
          status: "予定",
          date: "2025年Q1"
        }
      ]
    },
    {
      title: "フェーズ5: エコシステム拡大",
      description: "PulseChainエコシステムの拡大と機能強化",
      timeframe: "2025年Q2 - 2026年以降",
      status: "予定",
      progress: 0,
      color: theme.palette.secondary.main,
      icon: <TrendingUpIcon />,
      milestones: [
        {
          title: "クロスチェーン統合",
          description: "主要ブロックチェーンとの相互運用性の実現",
          status: "予定",
          date: "2025年Q2"
        },
        {
          title: "開発者助成金プログラム",
          description: "エコシステム拡大のための開発者支援プログラム",
          status: "予定",
          date: "2025年Q3"
        },
        {
          title: "エンタープライズソリューション",
          description: "企業向けのカスタムソリューション開発",
          status: "予定",
          date: "2025年Q4"
        },
        {
          title: "グローバル展開",
          description: "世界各地での採用拡大とローカライズ",
          status: "予定",
          date: "2026年以降"
        }
      ]
    }
  ];

  // 主要な技術マイルストーン
  const techMilestones = [
    {
      title: "リアルタイムトランザクション処理",
      description: "ブロックチェーンの概念を超えた、リアルタイムのトランザクション処理システム",
      icon: <SpeedIcon />,
      color: "#f44336", // red
      timeline: "2024年Q4",
      features: ["ミリ秒レベルの確定時間", "高スループット", "スケーラブルなアーキテクチャ"]
    },
    {
      title: "環境同期型コンセンサス",
      description: "自然環境と分散型データソースを活用した革新的なコンセンサスメカニズム",
      icon: <PublicIcon />,
      color: "#4caf50", // green
      timeline: "2024年Q2",
      features: ["多様なデータソース統合", "検証可能なランダム性", "操作耐性"]
    },
    {
      title: "ゼロエネルギーノード",
      description: "環境に優しい超低消費電力のノード運用技術",
      icon: <BatteryChargingFullIcon />,
      color: "#2196f3", // blue
      timeline: "2025年Q1",
      features: ["省電力設計", "再生可能エネルギー統合", "カーボンニュートラル"]
    },
    {
      title: "ダイナミックマイクロチェーン",
      description: "需要に応じて動的に生成・消滅するマイクロチェーン構造",
      icon: <StorageIcon />,
      color: "#ff9800", // orange
      timeline: "2025年Q2",
      features: ["動的スケーリング", "シャーディング", "高効率データ構造"]
    },
    {
      title: "人間的信頼形成システム",
      description: "ノードの協調性と行動履歴に基づく信頼スコアシステム",
      icon: <VerifiedUserIcon />,
      color: "#9c27b0", // purple
      timeline: "2025年Q3",
      features: ["信頼スコアリング", "悪意のあるノードの自動検出", "コミュニティガバナンス"]
    },
    {
      title: "ポスト量子暗号",
      description: "量子コンピュータによる攻撃に耐性を持つ暗号システム",
      icon: <SecurityIcon />,
      color: "#607d8b", // blue-grey
      timeline: "2024年Q3",
      features: ["CRYSTALS-Dilithium実装", "量子耐性", "長期的セキュリティ"]
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
              PulseChain ロードマップ
            </Typography>
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              sx={{ mb: 4, maxWidth: '800px' }}
            >
              革新的なブロックチェーン技術の開発から展開までの道のり
            </Typography>
          </motion.div>
        </Container>
      </Box>

      {/* メインコンテンツ */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Typography variant="h4" component="h2" gutterBottom>
                開発フェーズ
              </Typography>
              <Typography variant="body1" paragraph sx={{ mb: 4 }}>
                PulseChainの開発は複数のフェーズに分かれており、各フェーズで特定の目標を達成していきます。
                現在はフェーズ2の「テストネットとコミュニティ構築」段階にあります。
              </Typography>
            </motion.div>
            
            <Stepper orientation="vertical" sx={{ mb: 6 }}>
              {phases.map((phase, index) => (
                <Step key={index} active={phase.progress > 0} completed={phase.progress === 100}>
                  <StepLabel 
                    StepIconProps={{ 
                      icon: phase.icon,
                      style: { color: phase.color }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                      <Typography variant="h6" component="span">
                        {phase.title}
                      </Typography>
                      <Chip 
                        label={phase.status} 
                        size="small" 
                        color={
                          phase.status === "完了" ? "success" : 
                          phase.status === "進行中" ? "primary" : 
                          "default"
                        }
                        icon={phase.status === "完了" ? <CheckCircleIcon /> : <ScheduleIcon />}
                      />
                    </Box>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1" paragraph>
                        {phase.description}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>期間:</strong> {phase.timeframe}
                      </Typography>
                      <Box sx={{ mt: 1, mb: 2 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={phase.progress} 
                          sx={{ 
                            height: 8, 
                            borderRadius: 4,
                            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: phase.color
                            }
                          }} 
                        />
                        <Typography variant="body2" color="text.secondary" align="right" sx={{ mt: 0.5 }}>
                          {phase.progress}% 完了
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Typography variant="subtitle1" gutterBottom>
                      主要マイルストーン:
                    </Typography>
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      {phase.milestones.map((milestone, idx) => (
                        <Grid item xs={12} sm={6} md={3} key={idx}>
                          <Paper 
                            elevation={1} 
                            sx={{ 
                              p: 2, 
                              height: '100%',
                              borderLeft: `4px solid ${
                                milestone.status === "完了" ? theme.palette.success.main : 
                                milestone.status === "進行中" ? theme.palette.primary.main : 
                                theme.palette.action.disabled
                              }`
                            }}
                          >
                            <Typography variant="subtitle2" gutterBottom>
                              {milestone.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                              {milestone.description}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Chip 
                                label={milestone.status} 
                                size="small" 
                                variant="outlined"
                                color={
                                  milestone.status === "完了" ? "success" : 
                                  milestone.status === "進行中" ? "primary" : 
                                  "default"
                                }
                              />
                              <Typography variant="caption" color="text.secondary">
                                {milestone.date}
                              </Typography>
                            </Box>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 4 }} />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
                技術ロードマップ
              </Typography>
              
              <Grid container spacing={3}>
                {techMilestones.map((milestone, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card 
                      sx={{ 
                        height: '100%',
                        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-10px)',
                          boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                        }
                      }}
                      data-aos="fade-up"
                      data-aos-delay={index * 100}
                    >
                      <CardHeader
                        avatar={
                          <Avatar sx={{ bgcolor: milestone.color }}>
                            {milestone.icon}
                          </Avatar>
                        }
                        title={milestone.title}
                        subheader={`予定: ${milestone.timeline}`}
                      />
                      <CardContent>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {milestone.description}
                        </Typography>
                        <Typography variant="subtitle2" gutterBottom>
                          主な特徴:
                        </Typography>
                        <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                          {milestone.features.map((feature, idx) => (
                            <Box component="li" key={idx} sx={{ mb: 0.5 }}>
                              <Typography variant="body2">
                                {feature}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </motion.div>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Typography variant="h4" gutterBottom>
              PulseChainの未来を共に築きましょう
            </Typography>
            <Typography variant="body1" paragraph sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
              PulseChainは開発者、バリデーター、ユーザーなど、すべてのコミュニティメンバーの貢献によって成長します。
              今すぐ参加して、次世代のブロックチェーン技術の発展に貢献しましょう。
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
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
              <Button 
                variant="outlined" 
                color="primary" 
                size="large"
                component="a"
                href="https://github.com/enablerdao/PulseChain"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ 
                  fontWeight: 'bold',
                  px: 4,
                  py: 1.5,
                  borderRadius: 8,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: '0 10px 20px rgba(0,0,0,0.1)'
                  }
                }}
              >
                GitHubで貢献する
              </Button>
            </Box>
          </motion.div>
        </Box>
      </Container>
    </Box>
  );
};

export default Roadmap;