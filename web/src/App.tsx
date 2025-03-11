import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { useState, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import DataCollection from './pages/DataCollection';
import VerificationProcess from './pages/VerificationProcess';
import LiveDemo from './pages/LiveDemo';
import BecomeValidator from './pages/BecomeValidator';
import Roadmap from './pages/Roadmap';
import NetworkStats from './pages/NetworkStats';
import 'aos/dist/aos.css';
import AOS from 'aos';
import './App.css';

// カスタムテーマの作成
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6e8efb',
    },
    secondary: {
      main: '#a777e3',
    },
    background: {
      default: '#f9f9f9',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Helvetica Neue", Arial, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
        },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#8ca0ff',
    },
    secondary: {
      main: '#b68ae6',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Helvetica Neue", Arial, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
      },
    },
  },
});

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // AOSの初期化
    AOS.init({
      duration: 800,
      once: false,
      mirror: true,
      offset: 100,
    });
    
    // システムのダークモード設定を検出
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(prefersDarkMode);
    
    // スクロール時にAOSを更新
    window.addEventListener('scroll', () => {
      AOS.refresh();
    });
    
    return () => {
      window.removeEventListener('scroll', () => {
        AOS.refresh();
      });
    };
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <Router>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/data-collection" element={<DataCollection />} />
          <Route path="/verification-process" element={<VerificationProcess />} />
          <Route path="/live-demo" element={<LiveDemo />} />
          <Route path="/become-validator" element={<BecomeValidator />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/network-stats" element={<NetworkStats />} />
        </Routes>
        <Footer />
      </Router>
    </ThemeProvider>
  );
}

export default App;
