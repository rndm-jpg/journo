import {DetailPlace} from "@/interfaces/FlowInterface";
import PlaceCard from "@/components/PlaceCard";

interface PlaceCardsProps {
  places?: DetailPlace[]
}

export default function PlaceCards({places}: PlaceCardsProps) {
  if (!places) return <></>

  return <div className="row gy-5 mt-1">
    {places.map(place => {
      return <div className={"col-md-6 col-lg-4"} key={place.placeId}>
        <PlaceCard place={place}/>
      </div>
    })}
  </div>
}