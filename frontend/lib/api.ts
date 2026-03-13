export type DataProvenance = {
  data_source: string;
  is_fallback: boolean;
  data_complete: boolean;
  note: string | null;
};

export type Airport = {
  iata: string;
  airport_name: string;
  city: string | null;
  state: string | null;
  country: string;
};

export type AirportSearchResponse = {
  query: string;
  results: Airport[];
  metadata: DataProvenance;
};

export type RouteExploreCard = {
  destination: Airport;
  latest_route_attractiveness_score: number | null;
  latest_deal_signal: string | null;
  headline_fare_insight: string | null;
  reliability_summary: {
    avg_ontime_rate: number | null;
    avg_cancellation_rate: number | null;
  };
  score_confidence: number | null;
};

export type RouteExploreResponse = {
  origin: string;
  routes: RouteExploreCard[];
  metadata: DataProvenance;
};

export type RouteDetailResponse = {
  route_summary: {
    origin: Airport;
    destination: Airport;
  };
  monthly_fare_trend: {
    year: number;
    month: number;
    avg_fare_usd: number;
  }[];
  reliability_trend: {
    year: number;
    month: number;
    ontime_rate: number | null;
    cancellation_rate: number | null;
  }[];
  latest_score_breakdown: {
    year: number;
    month: number;
    reliability_score: number | null;
    fare_volatility: number | null;
    route_attractiveness_score: number | null;
    deal_signal: string;
  } | null;
  cheapest_month: {
    year: number;
    month: number;
    avg_fare_usd: number;
  } | null;
  methodology_hint: string;
  metadata: DataProvenance;
};

export type AirportContextResponse = {
  airport: Airport;
  latest_enplanement: {
    year: number;
    total_enplanements: number;
  } | null;
  related_routes: {
    destination_iata: string;
    destination_city: string | null;
    destination_airport_name: string;
    latest_route_attractiveness_score: number | null;
    latest_deal_signal: string | null;
  }[];
  metadata: DataProvenance;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const fallbackError = `Request failed (${response.status})`;
    let detail = fallbackError;

    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? fallbackError;
    } catch {
      detail = fallbackError;
    }

    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function searchAirports(query: string): Promise<AirportSearchResponse> {
  return apiFetch(`/airports/search?q=${encodeURIComponent(query)}`);
}

export function exploreRoutes(origin: string): Promise<RouteExploreResponse> {
  return apiFetch(`/routes/explore?origin=${encodeURIComponent(origin)}`);
}

export function getRouteDetail(origin: string, destination: string): Promise<RouteDetailResponse> {
  return apiFetch(`/routes/${encodeURIComponent(origin)}/${encodeURIComponent(destination)}`);
}

export function getAirportContext(iata: string): Promise<AirportContextResponse> {
  return apiFetch(`/airports/${encodeURIComponent(iata)}/context`);
}
