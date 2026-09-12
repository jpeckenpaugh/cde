import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { CorpusView } from './components/CorpusView';
import { SampleDetailView } from './components/SampleDetailView';
import { ReviewQueueView } from './components/ReviewQueueView';
import { ExportView } from './components/ExportView';
import { PdfViewerModal } from './components/PdfViewerModal';
import { IngestModal } from './components/IngestModal';
import { usePdfSearchParams } from './hooks/usePdfSearchParams';
import {
  fetchChapters,
  fetchSectionItems,
  fetchItem,
  fetchReviewQueue,
  fetchVerifiedExport,
  submitReview
} from './api/client';
import {
  ChapterHierarchy,
  AssessmentItem,
  ItemAnswerLink,
  VerifiedSampleExport,
  ReviewSubmission
} from './types';

export const App: React.FC = () => {
  const navigate = useNavigate();
  const { isPdfOpen, pdfDoc, pdfPage, openPdfPage, closePdf } = usePdfSearchParams();

  const [isIngestOpen, setIsIngestOpen] = useState<boolean>(false);
  const [chapters, setChapters] = useState<ChapterHierarchy[]>([]);
  const [reviewQueue, setReviewQueue] = useState<ItemAnswerLink[]>([]);
  const [verifiedSamples, setVerifiedSamples] = useState<VerifiedSampleExport[]>([]);

  const [isLoadingChapters, setIsLoadingChapters] = useState<boolean>(true);
  const [isLoadingQueue, setIsLoadingQueue] = useState<boolean>(false);
  const [isLoadingExport, setIsLoadingExport] = useState<boolean>(false);

  const loadChapters = async () => {
    setIsLoadingChapters(true);
    try {
      const data = await fetchChapters();
      setChapters(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingChapters(false);
    }
  };

  const loadQueue = async (status?: string) => {
    setIsLoadingQueue(true);
    try {
      const queue = await fetchReviewQueue(status);
      setReviewQueue(queue);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingQueue(false);
    }
  };

  const loadExports = async () => {
    setIsLoadingExport(true);
    try {
      const exports = await fetchVerifiedExport();
      setVerifiedSamples(exports);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingExport(false);
    }
  };

  const refreshGlobalCounts = async () => {
    await Promise.all([loadChapters(), loadQueue(), loadExports()]);
  };

  useEffect(() => {
    refreshGlobalCounts();
  }, []);

  const handleReviewSubmit = async (linkId: string, submission: ReviewSubmission) => {
    await submitReview(linkId, submission);
    await refreshGlobalCounts();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col font-sans">
      <Navbar
        reviewQueueCount={reviewQueue.length}
        verifiedCount={verifiedSamples.length}
        onOpenPdf={() => openPdfPage(1, '1')}
        onOpenIngest={() => setIsIngestOpen(true)}
      />

      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<DefaultCorpusRedirect chapters={chapters} isLoadingChapters={isLoadingChapters} />} />
          <Route path="/corpus" element={<DefaultCorpusRedirect chapters={chapters} isLoadingChapters={isLoadingChapters} />} />
          <Route
            path="/corpus/sections/:sectionId"
            element={
              <CorpusRouteWrapper
                chapters={chapters}
                isLoadingChapters={isLoadingChapters}
                onOpenPdfPage={openPdfPage}
                onReviewSubmit={handleReviewSubmit}
              />
            }
          />
          <Route
            path="/corpus/items/:itemId"
            element={
              <CorpusRouteWrapper
                chapters={chapters}
                isLoadingChapters={isLoadingChapters}
                onOpenPdfPage={openPdfPage}
                onReviewSubmit={handleReviewSubmit}
              />
            }
          />
          <Route
            path="/queue"
            element={
              <QueueRouteWrapper
                queue={reviewQueue}
                isLoadingQueue={isLoadingQueue}
                onRefreshQueue={loadQueue}
                onReviewSubmit={handleReviewSubmit}
              />
            }
          />
          <Route
            path="/export"
            element={<ExportView samples={verifiedSamples} isLoading={isLoadingExport} />}
          />
        </Routes>
      </main>

      {/* PDF Document Viewer Modal */}
      <PdfViewerModal
        isOpen={isPdfOpen}
        onClose={closePdf}
        initialPage={pdfPage}
        documentId={pdfDoc}
      />

      {/* Ingestion Control Modal */}
      <IngestModal
        isOpen={isIngestOpen}
        onClose={() => setIsIngestOpen(false)}
        onIngestComplete={refreshGlobalCounts}
      />
    </div>
  );
};

// Component to dynamically navigate to first available section
const DefaultCorpusRedirect: React.FC<{ chapters: ChapterHierarchy[]; isLoadingChapters: boolean }> = ({ chapters, isLoadingChapters }) => {
  if (isLoadingChapters) {
    return <div className="flex items-center justify-center h-48 text-gray-400 text-sm">Loading corpus...</div>;
  }
  const firstSectionId = chapters.find((ch) => ch.sections.length > 0)?.sections[0]?.id;
  if (firstSectionId) {
    return <Navigate to={`/corpus/sections/${firstSectionId}`} replace />;
  }
  return <Navigate to="/corpus/sections/none" replace />;
};

// Sub-component wrapper for Section and Item Corpus Routes
const CorpusRouteWrapper: React.FC<{
  chapters: ChapterHierarchy[];
  isLoadingChapters: boolean;
  onOpenPdfPage: (page: number, docId?: string) => void;
  onReviewSubmit: (linkId: string, submission: ReviewSubmission) => Promise<void>;
}> = ({ chapters, isLoadingChapters, onOpenPdfPage, onReviewSubmit }) => {
  const navigate = useNavigate();
  const { sectionId, itemId } = useParams<{ sectionId?: string; itemId?: string }>();

  const [sectionItems, setSectionItems] = useState<AssessmentItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<AssessmentItem | null>(null);
  const [isLoadingItems, setIsLoadingItems] = useState<boolean>(false);
  const [activeSectionId, setActiveSectionId] = useState<string>('');

  // Load items for section
  useEffect(() => {
    let secToLoad = sectionId;
    const allSections = chapters.flatMap((ch) => ch.sections);
    const sectionExists = allSections.some((sec) => sec.id === secToLoad);

    // Fallback if sectionId is missing, invalid (e.g. pre-reset UUID), legacy 'sec-1-1', or 'none'
    if (!secToLoad || !sectionExists || secToLoad === 'sec-1-1' || secToLoad === 'none') {
      const firstSec = allSections[0]?.id;
      if (firstSec && firstSec !== secToLoad) {
        secToLoad = firstSec;
        navigate(`/corpus/sections/${firstSec}`, { replace: true });
      }
    }

    if (secToLoad && secToLoad !== 'none' && secToLoad !== 'sec-1-1') {
      setActiveSectionId(secToLoad);
      setIsLoadingItems(true);
      fetchSectionItems(secToLoad)
        .then(setSectionItems)
        .catch((err) => {
          console.warn('Could not fetch section items:', secToLoad, err);
          setSectionItems([]);
        })
        .finally(() => setIsLoadingItems(false));
    } else {
      setSectionItems([]);
    }
  }, [sectionId, chapters]);

  // Load item detail modal if itemId parameter is in URL
  useEffect(() => {
    if (itemId) {
      fetchItem(itemId)
        .then((item) => {
          setSelectedItem(item);
          if (item.section_id && item.section_id !== activeSectionId) {
            setActiveSectionId(item.section_id);
            fetchSectionItems(item.section_id).then(setSectionItems).catch(console.error);
          }
        })
        .catch(console.error);
    } else {
      setSelectedItem(null);
    }
  }, [itemId]);

  const handleSelectSection = (secId: string) => {
    navigate(`/corpus/sections/${secId}`);
  };

  const handleSelectItem = (item: AssessmentItem) => {
    navigate(`/corpus/items/${item.id}`);
  };

  const handleCloseItemModal = () => {
    navigate(`/corpus/sections/${activeSectionId}`);
  };

  return (
    <>
      <CorpusView
        chapters={chapters}
        selectedSectionId={activeSectionId}
        onSelectSection={handleSelectSection}
        sectionItems={sectionItems}
        onSelectItem={handleSelectItem}
        isLoading={isLoadingChapters || isLoadingItems}
      />

      {selectedItem && (
        <SampleDetailView
          item={selectedItem}
          onClose={handleCloseItemModal}
          onReviewSubmit={onReviewSubmit}
          onOpenPdfPage={onOpenPdfPage}
        />
      )}
    </>
  );
};

// Sub-component wrapper for Queue Route
const QueueRouteWrapper: React.FC<{
  queue: ItemAnswerLink[];
  isLoadingQueue: boolean;
  onRefreshQueue: (status?: string) => Promise<void>;
  onReviewSubmit: (linkId: string, submission: ReviewSubmission) => Promise<void>;
}> = ({ queue, isLoadingQueue, onRefreshQueue, onReviewSubmit }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const statusFilter = searchParams.get('status') || '';

  const handleStatusFilterChange = (newStatus: string) => {
    if (newStatus) {
      setSearchParams({ status: newStatus });
    } else {
      setSearchParams({});
    }
  };

  useEffect(() => {
    onRefreshQueue(statusFilter || undefined);
  }, [statusFilter]);

  return (
    <ReviewQueueView
      queue={queue}
      selectedStatus={statusFilter}
      onStatusFilterChange={handleStatusFilterChange}
      onReviewSubmit={onReviewSubmit}
      isLoading={isLoadingQueue}
    />
  );
};

export default App;
