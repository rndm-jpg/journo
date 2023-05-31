import {DetailPlace} from "@/interfaces/FlowInterface";
import Image from "next/image";

interface PlaceCardProps {
  place: DetailPlace
}

export default function PlaceCard({place}: PlaceCardProps) {
  return <div className={`card h-100 shadow-sm position-relative pt-2 ${place.ignoredAt ? 'border-danger' : ''}`}>
    <div className="position-absolute top-0 w-100 translate-middle-y d-flex justify-content-end">
      {place.uploadedAt &&
          <a
              href={`https://postcard.inc/places/s/${place.placeId}`}
              target={"_blank"} rel={"noreferrer"}
              className="btn btn-sm text-white bg-black rounded-pill">
              Postcard
          </a>
      }
      {place.ignoredAt &&
          <div className="btn btn-sm btn-danger rounded-pill" title={place.ignoredReason}>
              IGNORED
          </div>
      }
      {place.gmaps &&
          <>
              <div style={{width: "10px"}}/>
              <a
                  href={place.gmaps}
                  target={"_blank"} rel={"noreferrer"}
                  className="btn btn-sm btn-primary rounded-pill">
                  Google Maps
              </a>
          </>
      }
    </div>
    <div className="card-body lh-1 pb-1 pt-3">
      <div className="small mb-2">
        <p className={"mb-0 small"}>{place.urlTitle}</p>
        <a href={place.url} target={"_blank"} rel={"noreferrer"} className={"text-primary"}>
          <small>
            {place.url}
          </small>
        </a>
      </div>
    </div>
    <div className="card-body position-relative p-0 flex-shrink-0" style={{
      height: "200px"
    }}>
      {place['media'].length > 0 &&
          <Image fill={true} style={{
            objectFit: 'cover'
          }} src={place['media'][0]['url']} alt={place['name']}/>
      }
      {place['media'].length === 0 &&
          <Image fill={true} style={{
            objectFit: 'cover'
          }} src={'https://via.placeholder.com/250x200.jpg'} alt={'placeholder image'}/>
      }
      <div className="position-absolute w-100 h-100 top-0 left-0 align-items-end d-flex" style={{
        background: "linear-gradient(0deg, rgba(0,0,0,.5) 0%, rgba(0,0,0,0) 50%)",
      }}>
        <div className="card-body text-white lh-1">
          <p className={"mb-0"}>{place.name}</p>
          <div className="small">
            <small>
              by {place.externalAttribution}
            </small>
            <br/>
            <small>
              Published at {new Date(place.externalPublishedAt).toLocaleDateString()}
            </small>
          </div>
        </div>
      </div>
    </div>
    <div className="card-header bg-transparent d-flex justify-content-around border-0 py-2">
      {!place.uploadedAt && !place.gmaps && !place.ignoredAt &&
          <button className="btn btn-outline-danger small btn-sm rounded-pill flex-fill">
              Not Uploaded
          </button>
      }
    </div>
    <div className="card-body h-100 small pt-0">
      <p className={"small"}>
        {place.ignoredReason}
      </p>
      {place.excerpt &&
          <p>
            {place.excerpt.split("\n").map((e, idx) => <p className={"mb-0"} key={idx}>{e}<br/></p>)}
          </p>
      }
      <p>
        {place.description.split("\n").map((e, idx) => <p className={"mb-0"} key={idx}>{e}<br/></p>)}
      </p>
    </div>
  </div>
}