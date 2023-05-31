"use client";

import {useCallback, useEffect, useState} from "react";
import axios from "axios";
import {ListFlowRoot} from "@/interfaces/FlowInterface";
import Link from "next/link";

interface FlowTableInterface {
  limit_per_page?: number
}

export default function FlowTable({limit_per_page = 6}: FlowTableInterface): JSX.Element {
  const [isFetched, setIsFetched] = useState(false);
  const [data, setData] = useState<ListFlowRoot | null>(null);
  const [fullyLoaded, setFullyLoad] = useState<boolean>(false);
  const [nextPage, setNextPage] = useState(1);

  const fetchNextPage = useCallback(async () => {
    await axios.get(`${process.env["NEXT_PUBLIC_API_URL"]}/dashboard/flow?page=${nextPage}&limit=${limit_per_page}`)
      .then(e => e.data as ListFlowRoot)
      .then(e => {
        if (e.data.length < e.limit) {
          setFullyLoad(true);
        }
        setNextPage(e.page + 1);
        setData(e);
      });
  }, [limit_per_page, nextPage]);

  useEffect(() => {
    if (!isFetched) {
      fetchNextPage().then(_ => setIsFetched(true));
    }
  }, [fetchNextPage, isFetched]);

  return <>
    <table className="table small align-middle">
      <thead>
        <tr>
          <th>ID</th>
          <th>Started At</th>
          <th>Source</th>
          <th>Total Page</th>
          <th>Total Places</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {!isFetched &&
          <tr>
            <td colSpan={7}>Loading...</td>
          </tr>
        }
        {isFetched && data?.data.map((datum) => (
          <tr key={datum.id}>
            <td>#{String(datum.id).padStart(4, "0")}</td>
            <td>{new Date(datum.createdAt).toLocaleString()}</td>
            <td>{datum.source.replace(/__/g, " - ").replace(/_/g, " ")}</td>
            <td>{datum.pages.success} of {datum.pages.success + datum.pages.ignored}</td>
            <td>{datum.places.success} of {datum.places.success + datum.places.ignored}</td>
            <td className={"text-center"}>
              <Link href={"/scrapings/" + datum.id} className="btn btn-primary btn-sm rounded-pill px-3">
              Details
              </Link>
            </td>
          </tr>
        ))}
      </tbody>
    </table>

    {!fullyLoaded && isFetched &&
      <p onClick={() => fetchNextPage()} className="fw-bold text-primary text-center btn">
        View More
      </p>
    }
  </>;
}