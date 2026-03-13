import Link from "next/link";

import { RouteExploreCard as RouteExploreCardType } from "@/lib/api";
import { formatLocation, formatPercent } from "@/lib/format";

type Props = {
  origin: string;
  route: RouteExploreCardType;
};

export function RouteExploreCard({ origin, route }: Props) {
  const scoreText = route.latest_route_attractiveness_score !== null ? route.latest_route_attractiveness_score.toFixed(1) : "N/A";

  return (
    <article className="route-card">
      <div className="route-card-top">
        <div>
          <h3>
            {route.destination.iata} · {route.destination.city ?? "Unknown city"}
          </h3>
          <p>{formatLocation(route.destination.city, route.destination.state, route.destination.country)}</p>
        </div>
        <div className="score-pill">Score {scoreText}</div>
      </div>

      <dl>
        <div>
          <dt>Deal signal</dt>
          <dd>{route.latest_deal_signal ?? "Not available"}</dd>
        </div>
        <div>
          <dt>Fare insight</dt>
          <dd>{route.headline_fare_insight ?? "No fare summary available"}</dd>
        </div>
        <div>
          <dt>On-time trend</dt>
          <dd>{formatPercent(route.reliability_summary.avg_ontime_rate)}</dd>
        </div>
        <div>
          <dt>Cancellation trend</dt>
          <dd>{formatPercent(route.reliability_summary.avg_cancellation_rate)}</dd>
        </div>
        <div>
          <dt>Score confidence</dt>
          <dd>{formatPercent(route.score_confidence)}</dd>
        </div>
      </dl>

      <Link href={`/routes/${origin}/${route.destination.iata}`} className="details-link">
        Inspect route
      </Link>
    </article>
  );
}
