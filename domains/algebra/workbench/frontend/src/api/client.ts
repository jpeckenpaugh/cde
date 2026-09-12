import {
  ChapterHierarchy,
  AssessmentItem,
  ItemAnswerLink,
  ReviewSubmission,
  VerifiedSampleExport
} from '../types';

const API_BASE = '/api';

export async function fetchChapters(): Promise<ChapterHierarchy[]> {
  const res = await fetch(`${API_BASE}/chapters`);
  if (!res.ok) throw new Error('Failed to fetch chapters');
  return res.json();
}

export async function fetchSectionItems(sectionId: string): Promise<AssessmentItem[]> {
  const res = await fetch(`${API_BASE}/sections/${sectionId}/items`);
  if (!res.ok) throw new Error('Failed to fetch section items');
  return res.json();
}

export async function fetchItem(itemId: string): Promise<AssessmentItem> {
  const res = await fetch(`${API_BASE}/items/${itemId}`);
  if (!res.ok) throw new Error('Failed to fetch item');
  return res.json();
}

export async function fetchReviewQueue(status?: string): Promise<ItemAnswerLink[]> {
  const url = status ? `${API_BASE}/review-queue?status=${encodeURIComponent(status)}` : `${API_BASE}/review-queue`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch review queue');
  return res.json();
}

export async function submitReview(linkId: string, submission: ReviewSubmission): Promise<ItemAnswerLink> {
  const res = await fetch(`${API_BASE}/links/${linkId}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(submission),
  });
  if (!res.ok) throw new Error('Failed to submit review');
  return res.json();
}

export async function fetchVerifiedExport(): Promise<VerifiedSampleExport[]> {
  const res = await fetch(`${API_BASE}/export/verified-samples`);
  if (!res.ok) throw new Error('Failed to fetch verified export');
  return res.json();
}
