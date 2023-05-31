import PostcardMain from "@/components/main/postcardMain";
import FlowTable from "@/components/FlowTable";

const ScrapingsPage = () => {
  return (
    <PostcardMain title={"Scrapings"}>
      <div className="card card-body">
        <FlowTable limit_per_page={10}/>
      </div>
    </PostcardMain>
  );
};

export default ScrapingsPage;
