"use client";

import PostcardMain from "@/components/main/postcardMain";
import FlowTable from "@/components/FlowTable";
import {ReactElement, useCallback, useEffect, useState} from "react";
import axios from "axios";
import {StatsFlow} from "@/interfaces/FlowInterface";

export default function Dashboard(): ReactElement {
  const [isFetched, setIsFetched] = useState(false);
  const [scrapingStats, setScrapingStats] = useState<[number, number, number]>([0, 0, 0])

  const fetchNextPage = useCallback(async () => {
    await axios.get(`${process.env["NEXT_PUBLIC_API_URL"]}/dashboard/flow/stats`)
      .then(e => e.data as StatsFlow)
      .then(e => {
        setScrapingStats([e.total_flow, e.total_success_page, e.total_success_place])
      });
  }, []);

  function numberWithCommas(x: number) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  useEffect(() => {
    if (!isFetched) {
      fetchNextPage().then(_ => setIsFetched(true));
    }
  }, [fetchNextPage, isFetched]);

  return (
    <PostcardMain title={"Content Dashboard"}>
      <div className="card card-body">
        <div className="row mb-5">
          <div className="col-4">
            <div className="card-body bg-light">
              <p className="h2">
                {numberWithCommas(scrapingStats[0])}
              </p>
              <small>
                Total Successful Scraping Flow
              </small>
            </div>
          </div>
          <div className="col-4">
            <div className="card-body bg-light">
              <p className="h2">
                {numberWithCommas(scrapingStats[1])}
              </p>
              <small>
                Total Successful URL Scrapes
              </small>
            </div>
          </div>
          <div className="col-4">
            <div className="card-body bg-light">
              <p className="h2">
                {numberWithCommas(scrapingStats[2])}
              </p>
              <small>
                Total Eligible Place Collected
              </small>
            </div>
          </div>
        </div>

        <h3 className="h5 mb-1">Recent Scrapings</h3>
        <p className="text-secondary small">Most recent automatic location scraping sessions</p>

        <FlowTable/>
      </div>
    </PostcardMain>
  );
}
