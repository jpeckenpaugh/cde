export interface SourceSpan {
  id: string;
  page_id: string;
  page_number?: number;
  text_content: string;
  reading_order: number;
  bbox_json?: string;
  extraction_metadata_json?: string;
}

export interface AnswerEntry {
  id: string;
  answer_label?: string;
  content_text: string;
  source_span_id?: string;
  source_span?: SourceSpan;
}

export interface ReviewEvent {
  id: string;
  link_id: string;
  action: string; // accept, reject, correct, mark_needs_resolution
  actor: string;
  timestamp: string;
  rationale?: string;
  target_answer_id?: string;
  target_answer?: AnswerEntry;
}

export interface ItemAnswerLink {
  id: string;
  item_id?: string;
  part_id?: string;
  answer_id: string;
  method: string;
  confidence: number;
  current_status: 'candidate' | 'reviewed' | 'verified' | 'rejected' | 'needs_resolution';
  answer?: AnswerEntry;
  review_events: ReviewEvent[];
  item?: AssessmentItem;
  part?: AssessmentPart;
}

export interface AssessmentPart {
  id: string;
  item_id: string;
  part_label: string;
  content_text: string;
  ordering: number;
  source_span_id?: string;
  source_span?: SourceSpan;
  links: ItemAnswerLink[];
}

export interface AssessmentItem {
  id: string;
  section_id: string;
  parent_item_id?: string;
  item_label: string;
  item_type: 'question' | 'worked_example' | 'try_it';
  content_text: string;
  ordering: number;
  source_span_id?: string;
  source_span?: SourceSpan;
  parts: AssessmentPart[];
  links: ItemAnswerLink[];
}

export interface SectionSummary {
  id: string;
  chapter_id: string;
  section_number: string;
  title: string;
  candidate_count: number;
  reviewed_count: number;
  verified_count: number;
  rejected_count: number;
  needs_resolution_count: number;
}

export interface ChapterHierarchy {
  id: string;
  chapter_number: number;
  title: string;
  sections: SectionSummary[];
}

export interface ReviewSubmission {
  action: 'accept' | 'reject' | 'correct' | 'mark_needs_resolution';
  actor: string;
  rationale?: string;
  replacement_answer_id?: string;
}

export interface VerifiedSampleExport {
  sample_id: string;
  link_id: string;
  item_type: string;
  item_label: string;
  part_label?: string;
  chapter_title: string;
  section_number: string;
  section_title: string;
  prompt_text: string;
  answer_text: string;
  verification_status: string;
  provenance: any;
}
