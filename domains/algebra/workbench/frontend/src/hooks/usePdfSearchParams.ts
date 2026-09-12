import { useSearchParams } from 'react-router-dom';

export interface PdfSearchState {
  isPdfOpen: boolean;
  pdfDoc: string; // documentId or filename, e.g. "1" or "elementary-algebra-2e_-_WEB.pdf"
  pdfPage: number;
  openPdfPage: (page: number, docId?: string) => void;
  closePdf: () => void;
}

export function usePdfSearchParams(): PdfSearchState {
  const [searchParams, setSearchParams] = useSearchParams();

  const pdfDocParam = searchParams.get('pdfDoc') || searchParams.get('pdfFile') || '';
  const pdfPageParam = searchParams.get('pdfPage');

  const pdfPage = pdfPageParam ? parseInt(pdfPageParam, 10) : 1;
  const isPdfOpen = Boolean(pdfDocParam || pdfPageParam);

  const openPdfPage = (page: number, docId: string = '1') => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set('pdfDoc', docId);
    nextParams.set('pdfPage', page.toString());
    setSearchParams(nextParams);
  };

  const closePdf = () => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete('pdfDoc');
    nextParams.delete('pdfFile');
    nextParams.delete('pdfPage');
    setSearchParams(nextParams);
  };

  return {
    isPdfOpen,
    pdfDoc: pdfDocParam || '1',
    pdfPage: isNaN(pdfPage) ? 1 : pdfPage,
    openPdfPage,
    closePdf
  };
}
