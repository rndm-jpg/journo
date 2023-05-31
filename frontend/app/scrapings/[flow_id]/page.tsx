"use client";

import {useCallback, useEffect, useState} from "react";
import {DetailPlace, ListPageByFlowIdRoot, ListPlaceByFlowIdRoot} from "@/interfaces/FlowInterface";
import axios from "axios";
import PlaceCards from "@/components/PlaceCards";
import Link from "next/link";
import PostcardMain from "@/components/main/postcardMain";

interface FlowPageProps {
  params: {
    flow_id: string
  },
}

const FlowPage = (props: FlowPageProps) => {
  const [initialFetched, setInitialFetched] = useState(false);

  const [data, setData] = useState<ListPageByFlowIdRoot | null>(null);

  const [cardData, setCardData] = useState<ListPlaceByFlowIdRoot | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [fullyLoaded, setFullyLoaded] = useState<boolean>(false);

  const [focusedSection, setFocusedSection] = useState<"URL" | "PLACES">("URL");

  const fetchListPageByFlowId = useCallback(async () => {
    await axios.get(`${process.env["NEXT_PUBLIC_API_URL"]}/dashboard/flow/${props.params.flow_id}`)
      .then(e => e.data as ListPageByFlowIdRoot)
      .then(e => {
        setData(e);
      });
  }, [props.params.flow_id]);

  const fetchCardPage = useCallback(async () => {
    await axios.get(`${process.env["NEXT_PUBLIC_API_URL"]}/dashboard/flow/${props.params.flow_id}/places?page=${currentPage}`)
      .then(e => e.data as ListPlaceByFlowIdRoot)
      .then(e => {
        if (e.data.length < e.limit) {
          setFullyLoaded(true);
        }

        let new_data: DetailPlace[] = [];
        if (cardData) {
          new_data = [...cardData.data];
        }
        new_data = [...new_data, ...e.data];

        e.data = [...new_data];

        setCardData(e);
        setCurrentPage(currentPage + 1);
      });
  }, [cardData, currentPage, props.params.flow_id]);

  const initialPageLoad = useCallback(async () => {
    await fetchListPageByFlowId();
    await fetchCardPage();
    setInitialFetched(true);
  }, [fetchCardPage, fetchListPageByFlowId]);

  useEffect(() => {
    if (initialFetched) return;
    initialPageLoad();
  }, [initialFetched, initialPageLoad]);


  function do_close() {
    setData(null);
    close();
  }

  if (!data) {
    return <>Loading...</>;
  }

  return (
    <PostcardMain 
      headtitle={"Scrapings"} 
      headurl={"/scrapings"}
      title={`Scraping Details #${String(props.params.flow_id).padStart(4, "0")}`}
    >
      <div className="row g-2">
        <div className="col-md-6 col-lg-3">
          <h6 className={"mb-0"}>Source</h6>
          <small>{data.source}</small>
        </div>
        <div className="col-md-6 col-lg-3">
          <h6 className={"mb-0"}>Start Time</h6>
          <small>{new Date(data.createdAt).toLocaleString()}</small>
        </div>
        <div className="col-md-6 col-lg-3">
          <h6 className={"mb-0"}>Total Pages</h6>
          <small>{data.pages.filter(page => !page.ignored_reason).length} of {data.pages.length}</small>
        </div>
        <div className="col-md-6 col-lg-3">
          <h6 className={"mb-0"}>Total Places</h6>
          <small>
            {data.pages.map(page => page.places.success).reduce((accumulator, currentValue) => accumulator + currentValue)}
            {" of "}
            {data.pages.map(page => page.places.success + page.places.ignored).reduce((accumulator, currentValue) => accumulator + currentValue)}
          </small>
        </div>
      </div>

      <div className="w-100 d-flex justify-content-end mt-3">
        <div className="btn-group" role="group">
          <button type="button" onClick={() => setFocusedSection("URL")}
            className={`btn btn-sm btn-${focusedSection === "URL" ? "" : "outline-"}primary`}>By URL
          </button>
          <button type="button" onClick={() => setFocusedSection("PLACES")}
            className={`btn btn-sm btn-${focusedSection === "PLACES" ? "" : "outline-"}primary`}>By Places
          </button>
        </div>
      </div>

      {focusedSection === "URL" &&
          <div className="table-responsive mt-2">
            <table className="table small align-middle table-bordered">
              <thead>
                <tr className={"align-middle text-center"}>
                  <th>Page URL</th>
                  <th>Total Places</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {!data &&
                  <tr>
                    <td colSpan={5}>Loading...</td>
                  </tr>
                }
                {
                  data.pages.map(page => (
                    <tr key={page.url}>
                      <td>
                        <p className={"mb-0 lh-1"}>
                          {page.title}
                        </p>
                        <small>
                          <a href={page.url} className={"text-primary"} target={"_blank"} rel={"noreferrer"}>
                            {page.url}
                          </a>
                        </small>
                      </td>
                      <td>{page.ignored_reason ? "-" : `${page.places.success} of ${page.places.success + page.places.ignored}`}</td>
                      <td>{page.ignored_reason ? `IGNORED: ${page.ignored_reason}` : "Normal"}</td>
                      <td className={"text-center"}>
                        <Link href={"/scrapings/by_url?url=" + page.url}
                          className="btn btn-primary btn-sm rounded-pill px-3 btn-sm">
                          Details
                        </Link>
                      </td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
          </div>
      }
      {focusedSection === "PLACES" &&
          <>
            <PlaceCards places={cardData?.data}/>

            {!fullyLoaded &&
                <div className="w-100 d-flex justify-content-center">
                  <p onClick={() => fetchCardPage()}
                    className="fw-bold text-primary text-center btn btn-outline-primary mt-3">
                        View More
                  </p>
                </div>
            }
          </>
      }
    </PostcardMain>
  );
};

export default FlowPage;