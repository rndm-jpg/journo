export interface ListFlowRoot {
  page: number
  limit: number
  data: ListFlowData[]
}

export interface ListFlowData {
  id: number
  source: string
  createdAt: string
  pages: SummaryCounter
  places: SummaryCounter
}

export interface SummaryCounter {
  success: number
  ignored: number
}

export interface ListPageByFlowIdRoot {
  source: string;
  id: number
  createdAt: string
  pages: ListPageByFlowIdData[]
}

export interface ListPlaceByFlowIdRoot {
  page: number
  limit: number
  data: DetailPlace[]
}

export interface StatsFlow {
  total_flow: number,
  total_success_page: number,
  total_success_place: number
}

export interface ListPageByFlowIdData {
  source: string;
  url: string
  true_url: string
  title: string
  ignored_reason: any
  places: SummaryCounter
}

export interface DetailPage {
  source: string
  url: string
  true_url: string
  createdAt: string
  parsedAt: string
  ignoredAt: any
  ignored_reason: any
  flow: number
  title: string
  description: string
  locations: string[]
  externalAttribution: string
  externalPublishedAt: string
  excerpt: string
  media: Media[]
  page_data: any
  places: DetailPlace[]
}

export interface Media {
  url: string,
  credit?: string,
}

export interface DetailPlace {
  id: string,
  page_url: string
  placeId: string
  name: string
  description: string
  excerpt: string
  media: Media[]
  externalAttribution: string
  externalPublishedAt: string
  urlTitle: string
  url: string
  lat: number
  long: number
  _extraData: object | null
  createdAt: string
  matchedAt: string
  serp_query: string
  ignoredAt: any
  ignoredReason: any
  uploadedAt: any
  pc_upload_result: {
    _id: string
  } | null
  mediaIds: any
  gmaps?: string
}
