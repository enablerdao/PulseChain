import { Box, Paper, Typography, useTheme } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface DataFlowStep {
  title: string;
  description: string;
  color?: string;
}

interface DataFlowDiagramProps {
  steps: DataFlowStep[];
}

const DataFlowDiagram = ({ steps }: DataFlowDiagramProps) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: { xs: 'column', md: 'row' }, 
      alignItems: 'center',
      justifyContent: 'center',
      gap: 2,
      my: 4,
      flexWrap: 'wrap'
    }}>
      {steps.map((step, index) => (
        <Box key={index} sx={{ display: 'flex', alignItems: 'center' }}>
          <Paper
            elevation={3}
            sx={{
              p: 2,
              minWidth: { xs: '100%', sm: '200px' },
              backgroundColor: step.color || theme.palette.primary.main,
              color: '#fff',
              textAlign: 'center',
              borderRadius: 2,
            }}
          >
            <Typography variant="h6" fontWeight="bold">
              {step.title}
            </Typography>
            <Typography variant="body2">
              {step.description}
            </Typography>
          </Paper>
          
          {index < steps.length - 1 && (
            <Box 
              sx={{ 
                display: { xs: 'none', md: 'flex' },
                mx: 2
              }}
            >
              <ArrowForwardIcon fontSize="large" color="action" />
            </Box>
          )}
          
          {index < steps.length - 1 && (
            <Box 
              sx={{ 
                display: { xs: 'flex', md: 'none' },
                my: 1,
                transform: 'rotate(90deg)'
              }}
            >
              <ArrowForwardIcon fontSize="large" color="action" />
            </Box>
          )}
        </Box>
      ))}
    </Box>
  );
};

export default DataFlowDiagram;