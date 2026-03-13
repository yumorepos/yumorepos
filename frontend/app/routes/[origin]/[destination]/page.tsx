"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { MetadataNotice } from "@/components/MetadataNotice";
import { SimpleLineChart } from "@/components/SimpleLineChart";
import { AirportContextResponse, RouteDetailResponse, getAirportContext, getRouteDetail } from "@/lib/api";
import { formatCurrency, formatLocation, formatMonth, formatPercent } from "@/lib/format";

type Props = {
  params: {
    origin: string;
    destination: string;
  };
};

export default function RouteDetailPage({ params }: Props) {
  const origin = params.origin.toUpperCase();
  const destination = params.destination.toUpperCase();

  const [route, setRoute] = useState<RouteDetailResponse | null>(null);
  const [context, setContext] = useState<AirportContextResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const routeData = await getRouteDetail(origin, destination);
        setRoute(routeData);

        try {
          const contextData = await getAirportContext(destination);
          setContext(contextData);
        } catch {
          setContext(null);
        }
      } catch (routeError) {
        setError(routeError instanceof Error ? routeError.message : "Unable to load route detail.");
        setRoute(null);
      } finally {
        setIsLoading(false);
      }
    };

    void load();
  }, [destination, origin]);

  const farePoints = useMemo(
    () =>
      route?.monthly_fare_trend.map((point) => ({
        label: formatMonth(point.year, point.month),
        value: point.avg_fare_usd,
      })) ?? [],
    [route?.monthly_fare_trend],
  );

  const reliabilityPoints = useMemo(
    () =>
      route?.reliability_trend.map((point) => ({
        label: formatMonth(point.year, point.month),
        value: point.ontime_rate,
      })) ?? [],
    [route?.reliability_trend],
  );

  return (
    <main className="page-shell">
      <Link href="/" className="back-link">
        ← Back to Route Explorer
      </Link>

      {isLoading ? <p className="status">Loading route detail…</p> : null}
      {error ? <p className="status error">Route detail error: {error}</p> : null}

      {route ? (
        <>
          <section className="hero compact">
            <p className="eyebrow">Route intelligence brief</p>
            <h1>
              {route.route_summary.origin.iata} → {route.route_summary.destination.iata}
            </h1>
            <p>
              {route.route_summary.origin.airport_name} to {route.route_summary.destination.airport_name}
            </p>
          </section>

          <MetadataNotice metadata={route.metadata} />

          <section className="metrics-grid">
            <article className="panel">
              <h3>Latest score breakdown</h3>
              {route.latest_score_breakdown ? (
                <dl className="kv-grid">
                  <div>
                    <dt>Route attractiveness</dt>
                    <dd>{route.latest_score_breakdown.route_attractiveness_score?.toFixed(1) ?? "Not available"}</dd>
                  </div>
                  <div>
                    <dt>Reliability score</dt>
                    <dd>{route.latest_score_breakdown.reliability_score?.toFixed(1) ?? "Not available"}</dd>
                  </div>
                  <div>
                    <dt>Fare volatility</dt>
                    <dd>{route.latest_score_breakdown.fare_volatility?.toFixed(2) ?? "Not available"}</dd>
                  </div>
                  <div>
                    <dt>Deal signal</dt>
                    <dd>{route.latest_score_breakdown.deal_signal}</dd>
                  </div>
                </dl>
              ) : (
                <p className="muted">Latest score record is not available for this route.</p>
              )}
            </article>

            <article className="panel">
              <h3>Cheapest month (observed)</h3>
              {route.cheapest_month ? (
                <>
                  <p className="callout">{formatMonth(route.cheapest_month.year, route.cheapest_month.month)}</p>
                  <p>{formatCurrency(route.cheapest_month.avg_fare_usd)} average observed fare.</p>
                </>
              ) : (
                <p className="muted">No cheapest month callout available yet.</p>
              )}
            </article>

            <article className="panel">
              <h3>Methodology hint</h3>
              <p>{route.methodology_hint}</p>
            </article>
          </section>

          <section className="chart-grid">
            <SimpleLineChart title="Monthly fare trend" points={farePoints} colorClassName="line-primary" valueFormatter={formatCurrency} />
            <SimpleLineChart
              title="On-time reliability trend"
              points={reliabilityPoints}
              colorClassName="line-secondary"
              valueFormatter={formatPercent}
            />
          </section>

          <section className="panel">
            <h3>Airport context</h3>
            {context ? (
              <>
                <p>
                  {context.airport.airport_name} · {formatLocation(context.airport.city, context.airport.state, context.airport.country)}
                </p>
                <p>
                  Latest enplanement: {context.latest_enplanement ? `${context.latest_enplanement.total_enplanements.toLocaleString()} (${context.latest_enplanement.year})` : "Not available"}
                </p>
                <div className="chips">
                  {context.related_routes.slice(0, 6).map((related) => (
                    <span key={`${related.destination_iata}-${related.destination_airport_name}`} className="chip">
                      {related.destination_iata} {related.latest_deal_signal ? `· ${related.latest_deal_signal}` : ""}
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <p className="muted">Airport context could not be loaded for this destination.</p>
            )}
          </section>
        </>
      ) : null}
    </main>
  );
}
