import { Box, Container, Typography, Link, useTheme } from '@mui/material';

const Footer = () => {
  const theme = useTheme();
  
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: theme.palette.mode === 'light' 
          ? theme.palette.grey[100] 
          : theme.palette.grey[900],
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' '}
          <Link color="inherit" href="#">
            PulseChain
          </Link>
          {' - 次世代のブロックチェーン技術'}
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;