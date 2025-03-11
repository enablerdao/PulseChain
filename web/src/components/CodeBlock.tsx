import { useTheme } from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeBlockProps {
  code: string;
  language?: string;
}

const CodeBlock = ({ code, language = 'javascript' }: CodeBlockProps) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';

  return (
    <SyntaxHighlighter
      language={language}
      style={isDarkMode ? tomorrow : oneLight}
      customStyle={{
        borderRadius: '8px',
        padding: '1rem',
        fontSize: '0.9rem',
        margin: '1rem 0',
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
};

export default CodeBlock;