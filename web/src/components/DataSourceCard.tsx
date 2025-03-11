import { Card, CardContent, CardHeader, Typography, Box, useTheme } from '@mui/material';
import CodeBlock from './CodeBlock';

interface DataSourceCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  sampleData?: string;
  language?: string;
}

const DataSourceCard = ({ 
  title, 
  description, 
  icon, 
  sampleData,
  language = 'json'
}: DataSourceCardProps) => {
  const theme = useTheme();
  
  return (
    <Card 
      elevation={3} 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.3s ease',
        '&:hover': {
          transform: 'translateY(-5px)',
        }
      }}
    >
      <CardHeader
        avatar={
          <Box sx={{ 
            color: theme.palette.primary.main,
            fontSize: '2rem'
          }}>
            {icon}
          </Box>
        }
        title={title}
        titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="body2" color="text.secondary" paragraph>
          {description}
        </Typography>
        
        {sampleData && (
          <>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
              サンプルデータ:
            </Typography>
            <CodeBlock code={sampleData} language={language} />
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default DataSourceCard;