#ifndef MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB
#define MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB

#include <AppAgent/EventChannel.h>
#include <MeqServer/VisHandlerNode.h>
#include <MeqServer/TID-MeqServer.h>
#include <VisCube/VisVocabulary.h>
#include <vector>
    
#pragma types #Meq::VisDataMux
#pragma aid Station Index Tile Format Start Pre Post Sync Chunks 

namespace Meq 
{

class Spigot;
class Sink;
  
//##ModelId=3F98DAE503DA
class VisDataMux : public Node
{
  public:
    //##ModelId=3F9FF71B006A
    VisDataMux ();
  
    virtual TypeId objectType() const
    { return TpMeqVisDataMux; }

    // redefined to check that children are Sinks and stepchildren are Spigots
    virtual void resolveChildren ();
    
    //##ModelId=3F98DAE6024A
    //##Documentation
    //## delivers visdata header to data mux
    int deliverHeader (const DMI::Record &header);
      
    //##ModelId=3F98DAE60251
    //##Documentation
    //## delivers tile to data mux
    //## rowrange specifies range of valid rows in tile
    int deliverTile (VisCube::VTile::Ref &tileref);

    //##Documentation
    //## delivers visdata footer to data mux
    int deliverFooter (const DMI::Record &footer);
    
    // helper func:
    // returns Meq::Cells object corresponding to a VisCube::VTile, plus range
    // of valid rows
    //##ModelId=3F9FF6970269
    void fillCells (Cells &cells,LoRange &range,const VisCube::VTile &tile);

    //##ModelId=3F98DAE60246
    LocalDebugContext;
    
  protected:
    void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    int  pollChildren (Result::Ref &resref,const Request &request);
    
  private:
    //##ModelId=3F9FF71B00C7
    VisDataMux (const VisDataMux &);

    void initInput (const DMI::Record &rec);
    void initOutput (const DMI::Record &rec);
    
    void clearOutput ();
    
    void postStatus ();
    
    int startSnippet (const VisCube::VTile &tile);
    int endSnippet   ();
    
    //##ModelId=3F992F280174
    static int formDataId (int sta1,int sta2)
    { return VisVocabulary::ifrNumber(sta1,sta2); }

    //##ModelId=3F99305003E3
    typedef std::set<VisHandlerNode *> HandlerSet;
    typedef std::set<int> IndexSet;
    
    //##ModelId=3F98DAE60247
    // set of all handlers for each data ID (==IFR)
    std::vector<HandlerSet> handlers_;
    // set of children numbers for each data ID (==IFR)
    std::vector<IndexSet> child_indices_;
    // set of flags: do we have a tile for this data ID (==IFR)
    std::vector<bool> have_tile_;
    
    //  list of columns to be added to output tiles
    //##ModelId=3FAA52A6008E
    typedef std::set<int> ColumnSet;
    ColumnSet output_columns_;
    
    // header is cached; it is dumped to output only if some tiles are being
    // written
    DMI::Record::Ref cached_header_;
    // flag: tiles are being written
    bool writing_data_;

    LoVec_double channel_freqs;
    LoVec_double channel_widths;  
    // flag: require a fully regular cells (single-segment)
    bool force_regular_grid;
    
    RequestId rqid_;
    Request::Ref current_req_;
    int current_seqnr_;
    LoRange current_range_;

    int num_chunks_;
    int num_tiles_;
    double time0_;          // start of first tile
    double tile_time_[2];   // range of current tile
    AppAgent::EventChannel::Ref  input_channel_;    
    AppAgent::EventChannel::Ref  output_channel_;    
};

} // namespace Meq

#endif /* MEQSERVER_SRC_SPIGOTMUX_H_HEADER_INCLUDED_82375EEB */
